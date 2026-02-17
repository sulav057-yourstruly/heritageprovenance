"""
Admin routes (admin only).
"""
import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import (
    ContributionRequest, User, Object, Submission, ActivityLog
)
from app.schemas import (
    ContributionRequestDetail, ApproveRequestRequest, RejectRequestRequest,
    ApproveSubmissionRequest, RejectSubmissionRequest, ActivityLogResponse,
    ItemCreate, ItemDetail
)
from app.auth import require_admin
from app.security import hash_password
from app.utils import log_activity, get_client_ip, OBJECTS_DIR, BASE_DIR
from app.crypto import compute_cid, derive_keypair_from_seed
from app.provenance import create_genesis_event

router = APIRouter(prefix="/admin", tags=["admin"])

# Contribution Request Management

@router.get("/requests", response_model=List[ContributionRequestDetail])
async def list_contribution_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all contribution requests."""
    query = db.query(ContributionRequest)
    if status_filter:
        query = query.filter(ContributionRequest.status == status_filter)
    
    requests = query.order_by(ContributionRequest.submitted_at.desc()).all()
    
    result = []
    for req in requests:
        photos = json.loads(req.sample_photos_json) if req.sample_photos_json else []
        references = json.loads(req.sample_references_json) if req.sample_references_json else []
        
        result.append(ContributionRequestDetail(
            request_id=req.request_id,
            email=req.email,
            name=req.name,
            bio=req.bio,
            affiliation=req.affiliation,
            reason=req.reason,
            sample_item_title=req.sample_item_title,
            sample_item_description=req.sample_item_description,
            sample_location=req.sample_location,
            sample_culture=req.sample_culture,
            sample_significance=req.sample_significance,
            sample_references=references,
            sample_photos=photos,
            status=req.status,
            submitted_at=req.submitted_at,
            reviewed_by=req.reviewed_by,
            reviewed_at=req.reviewed_at,
            admin_notes=req.admin_notes
        ))
    
    return result

@router.get("/requests/{request_id}", response_model=ContributionRequestDetail)
async def get_contribution_request(
    request_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get contribution request details."""
    req = db.query(ContributionRequest).filter(
        ContributionRequest.request_id == request_id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    photos = json.loads(req.sample_photos_json) if req.sample_photos_json else []
    references = json.loads(req.sample_references_json) if req.sample_references_json else []
    
    return ContributionRequestDetail(
        request_id=req.request_id,
        email=req.email,
        name=req.name,
        bio=req.bio,
        affiliation=req.affiliation,
        reason=req.reason,
        sample_item_title=req.sample_item_title,
        sample_item_description=req.sample_item_description,
        sample_location=req.sample_location,
        sample_culture=req.sample_culture,
        sample_significance=req.sample_significance,
        sample_references=references,
        sample_photos=photos,
        status=req.status,
        submitted_at=req.submitted_at,
        reviewed_by=req.reviewed_by,
        reviewed_at=req.reviewed_at,
        admin_notes=req.admin_notes
    )

@router.post("/requests/{request_id}/approve")
async def approve_contribution_request(
    request_id: str,
    request_data: ApproveRequestRequest,
    request_obj: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve contribution request, create user account, and publish sample item."""
    req = db.query(ContributionRequest).filter(
        ContributionRequest.request_id == request_id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != 'pending':
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Generate temporary password
    temp_password = str(uuid.uuid4())[:12]
    
    # Create user account
    user = User(
        user_id=str(uuid.uuid4()),
        email=req.email,
        password_hash=hash_password(temp_password),
        name=req.name,
        role='contributor',
        bio=req.bio,
        affiliation=req.affiliation,
        status='active',
        approved_by=admin.user_id,
        approved_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.flush()  # Get user_id
    
    # Create object from sample item
    object_id = str(uuid.uuid4())
    photos = json.loads(req.sample_photos_json) if req.sample_photos_json else []
    
    # Move photos from requests to objects directory
    primary_photo_path = None
    related_photos = []
    if photos:
        # Copy first photo as primary
        primary_photo_path = photos[0]
        related_photos = photos[1:] if len(photos) > 1 else []
    
    # Create object
    obj = Object(
        object_id=object_id,
        cid_sha256="",  # Will be set when file is processed
        bundle_manifest_json=json.dumps({
            "title": req.sample_item_title,
            "description": req.sample_item_description
        }),
        title=req.sample_item_title,
        description=req.sample_item_description,
        location=req.sample_location,
        culture=req.sample_culture,
        significance=req.sample_significance,
        keywords_json=json.dumps([]),
        references_json=req.sample_references_json,
        primary_photo_path=primary_photo_path,
        related_photos_json=json.dumps(related_photos) if related_photos else None,
        owner_id=user.user_id,
        visibility='public',  # Approved sample items are published
        published_at=datetime.now(timezone.utc),
        published_by=admin.user_id
    )
    db.add(obj)
    
    # Create genesis event
    actor_id = f"contributor-{user.user_id}"
    from app.models import Actor
    actor = db.query(Actor).filter(Actor.actor_id == actor_id).first()
    if not actor:
        _, pub_key = derive_keypair_from_seed(f"actor:{actor_id}")
        actor = Actor(
            actor_id=actor_id,
            name=req.name,
            pubkey_ed25519=pub_key
        )
        db.add(actor)
    
    _, private_key = derive_keypair_from_seed(f"actor:{actor_id}")
    create_genesis_event(
        db=db,
        object_id=object_id,
        event_type="INGESTION",
        payload={
            "cid": "sample-item",
            "title": req.sample_item_title,
            "description": req.sample_item_description
        },
        actor_id=actor_id,
        private_key_b64=private_key
    )
    
    # Update request
    req.status = 'approved'
    req.reviewed_by = admin.user_id
    req.reviewed_at = datetime.now(timezone.utc)
    req.admin_notes = request_data.admin_notes
    
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=admin.user_id,
        action_type="approve_request",
        resource_type="contribution_request",
        resource_id=request_id,
        details={"user_id": user.user_id, "temp_password": temp_password},
        ip_address=get_client_ip(request_obj)
    )
    
    return {
        "message": "Request approved",
        "user_id": user.user_id,
        "email": user.email,
        "temp_password": temp_password,
        "object_id": object_id
    }

@router.post("/requests/{request_id}/reject")
async def reject_contribution_request(
    request_id: str,
    request_data: RejectRequestRequest,
    request_obj: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject contribution request with reason."""
    req = db.query(ContributionRequest).filter(
        ContributionRequest.request_id == request_id
    ).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != 'pending':
        raise HTTPException(status_code=400, detail="Request already processed")
    
    req.status = 'rejected'
    req.reviewed_by = admin.user_id
    req.reviewed_at = datetime.now(timezone.utc)
    req.admin_notes = request_data.reason
    
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=admin.user_id,
        action_type="reject_request",
        resource_type="contribution_request",
        resource_id=request_id,
        details={"reason": request_data.reason},
        ip_address=get_client_ip(request_obj)
    )
    
    return {"message": "Request rejected"}

# Submission Management

@router.get("/submissions", response_model=List[dict])
async def list_submissions(
    status_filter: Optional[str] = Query(None, alias="status"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all submissions."""
    query = db.query(Submission)
    if status_filter:
        query = query.filter(Submission.status == status_filter)
    
    submissions = query.order_by(Submission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        obj = db.query(Object).filter(Object.object_id == sub.object_id).first()
        submitter = db.query(User).filter(User.user_id == sub.submitted_by).first()
        
        result.append({
            "submission_id": sub.submission_id,
            "object_id": sub.object_id,
            "object_title": obj.title if obj else None,
            "submitted_by": sub.submitted_by,
            "submitter_name": submitter.name if submitter else None,
            "submission_type": sub.submission_type,
            "status": sub.status,
            "submitted_at": sub.submitted_at,
            "reviewed_by": sub.reviewed_by,
            "reviewed_at": sub.reviewed_at,
            "admin_feedback": sub.admin_feedback
        })
    
    return result

@router.post("/submissions/{submission_id}/approve")
async def approve_submission(
    submission_id: str,
    request_data: ApproveSubmissionRequest,
    request_obj: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve submission and make item public."""
    sub = db.query(Submission).filter(Submission.submission_id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if sub.status != 'pending':
        raise HTTPException(status_code=400, detail="Submission already processed")
    
    obj = db.query(Object).filter(Object.object_id == sub.object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # Make public
    obj.visibility = 'public'
    obj.published_at = datetime.now(timezone.utc)
    obj.published_by = admin.user_id
    
    # Update submission
    sub.status = 'approved'
    sub.reviewed_by = admin.user_id
    sub.reviewed_at = datetime.now(timezone.utc)
    sub.admin_feedback = request_data.admin_feedback
    
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=admin.user_id,
        action_type="approve_submission",
        resource_type="submission",
        resource_id=submission_id,
        details={"object_id": sub.object_id},
        ip_address=get_client_ip(request_obj)
    )
    
    return {"message": "Submission approved", "object_id": sub.object_id}

@router.post("/submissions/{submission_id}/reject")
async def reject_submission(
    submission_id: str,
    request_data: RejectSubmissionRequest,
    request_obj: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject submission with feedback."""
    sub = db.query(Submission).filter(Submission.submission_id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if sub.status != 'pending':
        raise HTTPException(status_code=400, detail="Submission already processed")
    
    sub.status = 'rejected'
    sub.reviewed_by = admin.user_id
    sub.reviewed_at = datetime.now(timezone.utc)
    sub.admin_feedback = request_data.admin_feedback
    
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        user_id=admin.user_id,
        action_type="reject_submission",
        resource_type="submission",
        resource_id=submission_id,
        details={"feedback": request_data.admin_feedback},
        ip_address=get_client_ip(request_obj)
    )
    
    return {"message": "Submission rejected"}

# Activity Logs

@router.get("/logs", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    action_type: Optional[str] = Query(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get activity logs."""
    query = db.query(ActivityLog)
    
    if action_type:
        query = query.filter(ActivityLog.action_type == action_type)
    
    logs = query.order_by(ActivityLog.timestamp.desc()).offset(offset).limit(limit).all()
    
    result = []
    for log in logs:
        details = json.loads(log.details_json) if log.details_json else None
        result.append(ActivityLogResponse(
            log_id=log.log_id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            action_type=log.action_type,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=details
        ))
    
    return result

@router.get("/stats")
async def get_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    total_items = db.query(Object).filter(Object.visibility == 'public').count()
    total_contributors = db.query(User).filter(User.role == 'contributor', User.status == 'active').count()
    pending_requests = db.query(ContributionRequest).filter(ContributionRequest.status == 'pending').count()
    pending_submissions = db.query(Submission).filter(Submission.status == 'pending').count()
    
    return {
        "total_items": total_items,
        "total_contributors": total_contributors,
        "pending_requests": pending_requests,
        "pending_submissions": pending_submissions
    }
