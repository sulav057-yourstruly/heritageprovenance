"""
Contributor routes (require contributor or admin login).
"""
import uuid
import json
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Object, Submission, User
from app.schemas import ItemCreate, SubmissionResponse, ItemDetail
from app.auth import require_contributor
from app.utils import save_photo, log_activity, get_client_ip, OBJECTS_DIR, BASE_DIR
from app.crypto import compute_cid, derive_keypair_from_seed
from app.provenance import create_genesis_event
from app.models import Actor

router = APIRouter(prefix="/my", tags=["contributor"])

@router.get("/contributions", response_model=List[ItemDetail])
async def my_contributions(
    user: User = Depends(require_contributor),
    db: Session = Depends(get_db)
):
    """List my submitted items."""
    items = db.query(Object).filter(Object.owner_id == user.user_id).all()
    
    result = []
    for item in items:
        keywords = json.loads(item.keywords_json) if item.keywords_json else None
        references = json.loads(item.references_json) if item.references_json else None
        related_photos = json.loads(item.related_photos_json) if item.related_photos_json else None
        
        result.append(ItemDetail(
            object_id=item.object_id,
            title=item.title or "Untitled",
            description=item.description,
            heritage_type=item.heritage_type,
            location=item.location,
            date_created=item.date_created,
            culture=item.culture,
            significance=item.significance,
            keywords=keywords,
            references=references,
            primary_photo_path=item.primary_photo_path,
            related_photos=related_photos,
            created_at=item.created_at,
            published_at=item.published_at
        ))
    
    return result

@router.get("/submissions", response_model=List[dict])
async def my_submissions(
    user: User = Depends(require_contributor),
    db: Session = Depends(get_db)
):
    """List my submission history."""
    submissions = db.query(Submission).filter(
        Submission.submitted_by == user.user_id
    ).order_by(Submission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        obj = db.query(Object).filter(Object.object_id == sub.object_id).first()
        result.append({
            "submission_id": sub.submission_id,
            "object_id": sub.object_id,
            "object_title": obj.title if obj else None,
            "submission_type": sub.submission_type,
            "status": sub.status,
            "submitted_at": sub.submitted_at,
            "reviewed_at": sub.reviewed_at,
            "admin_feedback": sub.admin_feedback
        })
    
    return result

@router.post("/items", response_model=SubmissionResponse)
async def submit_item(
    request_obj: Request,
    title: str = Form(...),
    description: str = Form(...),
    heritage_type: str = Form(None),
    location: str = Form(None),
    date_created: str = Form(None),
    culture: str = Form(None),
    significance: str = Form(None),
    keywords: str = Form(None),  # JSON array as string
    references: str = Form(None),  # JSON array as string
    primary_photo: UploadFile = File(...),
    related_photos: list[UploadFile] = File(None),
    user: User = Depends(require_contributor),
    db: Session = Depends(get_db)
):
    """Submit new item for review."""
    
    # Read and save primary photo
    primary_content = await primary_photo.read()
    primary_path = save_photo(primary_content, OBJECTS_DIR, primary_photo.filename)
    
    # Compute CID from primary photo
    cid = compute_cid(primary_content)
    
    # Save related photos
    related_photo_paths = []
    if related_photos:
        for photo in related_photos[:5]:
            content = await photo.read()
            path = save_photo(content, OBJECTS_DIR, photo.filename)
            related_photo_paths.append(path)
    
    # Parse JSON fields
    keywords_list = []
    if keywords:
        try:
            keywords_list = json.loads(keywords)
        except:
            pass
    
    references_list = []
    if references:
        try:
            references_list = json.loads(references)
        except:
            pass
    
    # Create object
    object_id = str(uuid.uuid4())
    
    obj = Object(
        object_id=object_id,
        cid_sha256=cid,
        bundle_manifest_json=json.dumps({
            "title": title,
            "description": description
        }),
        title=title,
        description=description,
        heritage_type=heritage_type,
        location=location,
        date_created=date_created,
        culture=culture,
        significance=significance,
        keywords_json=json.dumps(keywords_list) if keywords_list else None,
        references_json=json.dumps(references_list) if references_list else None,
        primary_photo_path=primary_path,
        related_photos_json=json.dumps(related_photo_paths) if related_photo_paths else None,
        owner_id=user.user_id,
        visibility='private'  # Starts private, admin approves to make public
    )
    db.add(obj)
    db.flush()
    
    # Create genesis event
    actor_id = f"contributor-{user.user_id}"
    actor = db.query(Actor).filter(Actor.actor_id == actor_id).first()
    if not actor:
        _, pub_key = derive_keypair_from_seed(f"actor:{actor_id}")
        actor = Actor(
            actor_id=actor_id,
            name=user.name,
            pubkey_ed25519=pub_key
        )
        db.add(actor)
    
    _, private_key = derive_keypair_from_seed(f"actor:{actor_id}")
    create_genesis_event(
        db=db,
        object_id=object_id,
        event_type="INGESTION",
        payload={
            "cid": cid,
            "title": title,
            "description": description
        },
        actor_id=actor_id,
        private_key_b64=private_key
    )
    
    # Create submission
    submission = Submission(
        submission_id=str(uuid.uuid4()),
        object_id=object_id,
        submitted_by=user.user_id,
        submission_type='new_item',
        status='pending'
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Log activity
    log_activity(
        db=db,
        user_id=user.user_id,
        action_type="submit_item",
        resource_type="submission",
        resource_id=submission.submission_id,
        details={"object_id": object_id},
        ip_address=get_client_ip(request_obj)
    )
    
    return SubmissionResponse(
        submission_id=submission.submission_id,
        object_id=submission.object_id,
        status=submission.status,
        submitted_at=submission.submitted_at
    )

@router.get("/items/{object_id}", response_model=ItemDetail)
async def get_my_item(
    object_id: str,
    user: User = Depends(require_contributor),
    db: Session = Depends(get_db)
):
    """Get my item details."""
    item = db.query(Object).filter(
        Object.object_id == object_id,
        Object.owner_id == user.user_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    keywords = json.loads(item.keywords_json) if item.keywords_json else None
    references = json.loads(item.references_json) if item.references_json else None
    related_photos = json.loads(item.related_photos_json) if item.related_photos_json else None
    
    return ItemDetail(
        object_id=item.object_id,
        title=item.title or "Untitled",
        description=item.description,
        heritage_type=item.heritage_type,
        location=item.location,
        date_created=item.date_created,
        culture=item.culture,
        significance=item.significance,
        keywords=keywords,
        references=references,
        primary_photo_path=item.primary_photo_path,
        related_photos=related_photos,
        created_at=item.created_at,
        published_at=item.published_at
    )
