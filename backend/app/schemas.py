"""
Pydantic request/response schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Actor schemas
class ActorCreate(BaseModel):
    actor_id: str
    name: str
    pubkey_ed25519: str = ""  # Base64 encoded, optional - will be derived if not provided

class ActorResponse(BaseModel):
    actor_id: str
    name: str
    pubkey_ed25519: str
    created_at: datetime

# Ingest schemas
class IngestRequest(BaseModel):
    metadata: Dict[str, Any]  # Dublin Core / PREMIS fields
    actor_id: str

class IngestResponse(BaseModel):
    object_id: str
    cid: str
    genesis_event_hash: str

# Event schemas
class EventCreate(BaseModel):
    event_type: str  # INGESTION, METADATA_EDIT, MIGRATION, CUSTODY_TRANSFER
    payload: Dict[str, Any]
    actor_id: str

class EventResponse(BaseModel):
    event_hash: str

# Anchor schemas
class AnchorResponse(BaseModel):
    batch_id: str
    merkle_root: str
    anchored_at: datetime
    event_count: int

# Verify schemas
class VerifyRequest(BaseModel):
    pass  # File will be uploaded as multipart

class EventTimelineItem(BaseModel):
    event_hash: str
    event_type: str
    timestamp: datetime
    actor_id: str
    payload: Dict[str, Any]
    prev_event_hash: Optional[str]
    signature_valid: bool
    anchored: bool
    batch_id: Optional[str]

class VerificationReport(BaseModel):
    cid_match: bool
    chain_valid: bool
    signatures_valid: bool
    anchored: bool
    timeline: List[EventTimelineItem]
    errors: List[str]

# JSON-LD export (will be returned as raw JSON, not Pydantic model)

# Auth schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    
    class Config:
        from_attributes = True

# Gallery schemas
class ItemSummary(BaseModel):
    object_id: str
    title: str
    heritage_type: Optional[str] = None
    location: Optional[str] = None
    culture: Optional[str] = None
    primary_photo_path: Optional[str] = None
    date_created: Optional[str] = None
    
    class Config:
        from_attributes = True

class ItemDetail(ItemSummary):
    description: Optional[str] = None
    significance: Optional[str] = None
    keywords: Optional[List[str]] = None
    references: Optional[List[str]] = None
    related_photos: Optional[List[str]] = None
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Contribution request schemas
class ContributionRequestCreate(BaseModel):
    email: str
    name: str
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    reason: str
    sample_item_title: str
    sample_item_description: str
    sample_location: Optional[str] = None
    sample_culture: Optional[str] = None
    sample_significance: Optional[str] = None
    sample_references: Optional[List[str]] = None

class ContributionRequestResponse(BaseModel):
    request_id: str
    email: str
    name: str
    status: str
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# Item submission schemas
class ItemCreate(BaseModel):
    title: str
    description: str
    heritage_type: Optional[str] = None
    location: Optional[str] = None
    date_created: Optional[str] = None
    culture: Optional[str] = None
    significance: Optional[str] = None
    keywords: Optional[List[str]] = None
    references: Optional[List[str]] = None

class SubmissionResponse(BaseModel):
    submission_id: str
    object_id: str
    status: str
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# Admin schemas
class ContributionRequestDetail(ContributionRequestResponse):
    bio: Optional[str] = None
    affiliation: Optional[str] = None
    reason: str
    sample_item_title: str
    sample_item_description: str
    sample_location: Optional[str] = None
    sample_culture: Optional[str] = None
    sample_significance: Optional[str] = None
    sample_references: Optional[List[str]] = None
    sample_photos: List[str]
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class ApproveRequestRequest(BaseModel):
    admin_notes: Optional[str] = None

class RejectRequestRequest(BaseModel):
    reason: str

class ApproveSubmissionRequest(BaseModel):
    admin_feedback: Optional[str] = None

class RejectSubmissionRequest(BaseModel):
    admin_feedback: str

class ActivityLogResponse(BaseModel):
    log_id: str
    timestamp: datetime
    user_id: Optional[str] = None
    action_type: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True