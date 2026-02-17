"""
Contribution request routes (public).
"""
import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ContributionRequest, User, Object
from app.schemas import ContributionRequestCreate, ContributionRequestResponse
from app.utils import save_photo, log_activity, get_client_ip, REQUESTS_DIR, BASE_DIR
from app.crypto import compute_cid, derive_keypair_from_seed
from app.provenance import create_genesis_event

router = APIRouter(prefix="/contribute", tags=["contribute"])

@router.post("/request", response_model=ContributionRequestResponse)
async def submit_contribution_request(
    request: Request,
    email: str = Form(...),
    name: str = Form(...),
    bio: str = Form(None),
    affiliation: str = Form(None),
    reason: str = Form(...),
    sample_item_title: str = Form(...),
    sample_item_description: str = Form(...),
    sample_location: str = Form(None),
    sample_culture: str = Form(None),
    sample_significance: str = Form(None),
    sample_references: str = Form(None),  # JSON array as string
    primary_photo: UploadFile = File(...),
    related_photos: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db)
):
    """Submit a contribution request with sample item."""
    
    # Validate email not already used
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate request not already pending
    pending = db.query(ContributionRequest).filter(
        ContributionRequest.email == email,
        ContributionRequest.status == 'pending'
    ).first()
    if pending:
        raise HTTPException(status_code=400, detail="You already have a pending request")
    
    request_id = str(uuid.uuid4())
    
    # Save photos
    photo_paths = []
    
    # Primary photo
    primary_content = await primary_photo.read()
    primary_path = save_photo(primary_content, REQUESTS_DIR, primary_photo.filename)
    photo_paths.append(primary_path)
    
    # Related photos (max 5)
    if related_photos:
        for i, photo in enumerate(related_photos[:5]):
            content = await photo.read()
            path = save_photo(content, REQUESTS_DIR, photo.filename)
            photo_paths.append(path)
    
    # Parse references
    references_list = []
    if sample_references:
        try:
            references_list = json.loads(sample_references)
        except:
            pass
    
    # Create request
    contribution_request = ContributionRequest(
        request_id=request_id,
        email=email,
        name=name,
        bio=bio,
        affiliation=affiliation,
        reason=reason,
        sample_item_title=sample_item_title,
        sample_item_description=sample_item_description,
        sample_location=sample_location,
        sample_culture=sample_culture,
        sample_significance=sample_significance,
        sample_references_json=json.dumps(references_list) if references_list else None,
        sample_photos_json=json.dumps(photo_paths),
        status='pending'
    )
    
    db.add(contribution_request)
    db.commit()
    db.refresh(contribution_request)
    
    # Log activity
    log_activity(
        db=db,
        user_id=None,
        action_type="request_contribution",
        resource_type="contribution_request",
        resource_id=request_id,
        ip_address=get_client_ip(request)
    )
    
    return ContributionRequestResponse(
        request_id=contribution_request.request_id,
        email=contribution_request.email,
        name=contribution_request.name,
        status=contribution_request.status,
        submitted_at=contribution_request.submitted_at
    )
