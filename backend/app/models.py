"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, CheckConstraint
from sqlalchemy.sql import func
from app.db import Base

class Actor(Base):
    """Actor (institution/curator) with public key."""
    __tablename__ = "actors"
    
    actor_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    pubkey_ed25519 = Column(String, nullable=False)  # Base64 encoded
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    """User account (contributors and admin)."""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default='contributor', nullable=False)  # 'contributor' or 'admin'
    bio = Column(Text, nullable=True)
    affiliation = Column(Text, nullable=True)
    status = Column(String, default='active', nullable=False)  # 'active' or 'suspended'
    approved_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        CheckConstraint("role IN ('contributor', 'admin')", name='check_role'),
        CheckConstraint("status IN ('active', 'suspended')", name='check_status'),
    )

class ContributionRequest(Base):
    """Contribution request from visitors wanting to become contributors."""
    __tablename__ = "contribution_requests"
    
    request_id = Column(String, primary_key=True)
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    affiliation = Column(Text, nullable=True)
    reason = Column(Text, nullable=False)
    sample_item_title = Column(String, nullable=False)
    sample_item_description = Column(Text, nullable=False)
    sample_location = Column(String, nullable=True)
    sample_culture = Column(String, nullable=True)
    sample_significance = Column(Text, nullable=True)
    sample_references_json = Column(Text, nullable=True)  # JSON array
    sample_photos_json = Column(Text, nullable=False)  # JSON array of file paths
    status = Column(String, default='pending', nullable=False, index=True)  # 'pending', 'approved', 'rejected'
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name='check_request_status'),
    )

class Object(Base):
    """Digital heritage object."""
    __tablename__ = "objects"
    
    object_id = Column(String, primary_key=True)
    cid_sha256 = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bundle_manifest_json = Column(Text, nullable=False)  # JSON string
    
    # Enhanced fields for heritage archive
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    heritage_type = Column(String, nullable=True)  # 'artifact', 'photograph', 'manuscript', 'artwork', 'architecture'
    location = Column(String, nullable=True)
    date_created = Column(String, nullable=True)  # e.g., '17th century' or '1920'
    culture = Column(String, nullable=True)  # e.g., 'Newar', 'Tibetan Buddhist'
    significance = Column(Text, nullable=True)
    keywords_json = Column(Text, nullable=True)  # JSON array
    references_json = Column(Text, nullable=True)  # JSON array of citations
    
    # Media
    primary_photo_path = Column(String, nullable=True)
    related_photos_json = Column(Text, nullable=True)  # JSON array of file paths
    
    # Ownership and visibility
    owner_id = Column(String, ForeignKey("users.user_id"), nullable=True, index=True)
    visibility = Column(String, default='private', nullable=False, index=True)  # 'private' or 'public'
    
    # Publication metadata
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    published_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    
    __table_args__ = (
        CheckConstraint("visibility IN ('private', 'public')", name='check_visibility'),
    )

class Submission(Base):
    """Contributor submissions awaiting admin approval."""
    __tablename__ = "submissions"
    
    submission_id = Column(String, primary_key=True)
    object_id = Column(String, ForeignKey("objects.object_id"), nullable=False, index=True)
    submitted_by = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    submission_type = Column(String, default='new_item', nullable=False)  # 'new_item' or 'edit_suggestion'
    status = Column(String, default='pending', nullable=False, index=True)  # 'pending', 'approved', 'rejected'
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    admin_feedback = Column(Text, nullable=True)
    
    __table_args__ = (
        CheckConstraint("submission_type IN ('new_item', 'edit_suggestion')", name='check_submission_type'),
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name='check_submission_status'),
    )

class ActivityLog(Base):
    """System activity logs for admin monitoring."""
    __tablename__ = "activity_logs"
    
    log_id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True, index=True)
    action_type = Column(String, nullable=False)  # 'request_contribution', 'approve_request', 'submit_item', etc.
    resource_type = Column(String, nullable=True)  # 'contribution_request', 'object', 'submission', 'event'
    resource_id = Column(String, nullable=True)
    details_json = Column(Text, nullable=True)  # JSON object
    ip_address = Column(String, nullable=True)

class Event(Base):
    """Provenance event (append-only chain)."""
    __tablename__ = "events"
    
    event_hash = Column(String, primary_key=True)
    object_id = Column(String, ForeignKey("objects.object_id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # INGESTION, METADATA_EDIT, MIGRATION, CUSTODY_TRANSFER
    prev_event_hash = Column(String, nullable=True)  # NULL for genesis
    timestamp = Column(DateTime(timezone=True), nullable=False)
    actor_id = Column(String, ForeignKey("actors.actor_id"), nullable=False)
    payload_json = Column(Text, nullable=False)  # JSON string
    signature_b64 = Column(String, nullable=False)  # Base64 encoded Ed25519 signature

class AnchorProof(Base):
    """Merkle inclusion proof for anchored events."""
    __tablename__ = "anchor_proofs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_hash = Column(String, ForeignKey("events.event_hash"), nullable=False, index=True)
    batch_id = Column(String, nullable=False, index=True)
    merkle_root = Column(String, nullable=False)
    proof_path = Column(Text, nullable=False)  # JSON array of hashes for inclusion proof
    anchored_at = Column(DateTime(timezone=True), nullable=False)

