"""
Provenance event chain logic: prev_event_hash linking, append-only guarantees.
"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Event, Object
from app.crypto import hash_event, sign_event
from datetime import datetime

def get_latest_event(db: Session, object_id: str) -> Optional[Event]:
    """Get the most recent event for an object (by timestamp)."""
    return db.query(Event).filter(
        Event.object_id == object_id
    ).order_by(Event.timestamp.desc()).first()

def create_genesis_event(
    db: Session,
    object_id: str,
    event_type: str,
    payload: dict,
    actor_id: str,
    private_key_b64: str
) -> Event:
    """
    Create genesis event (first event for an object, no prev_event_hash).
    """
    # Get a single timestamp and use it for both signing and storing
    # This ensures the stored timestamp matches exactly what was signed
    from datetime import timezone
    timestamp_utc = datetime.now(timezone.utc)
    
    # Convert to timezone-naive UTC for signing (matches datetime.utcnow() behavior)
    # This ensures consistent canonical JSON representation
    timestamp_for_signing = timestamp_utc.replace(tzinfo=None).isoformat()
    
    event_data = {
        "object_id": object_id,
        "event_type": event_type,
        "prev_event_hash": None,
        "timestamp": timestamp_for_signing,
        "actor_id": actor_id,
        "payload": payload
    }
    
    event_hash = hash_event(event_data)
    signature = sign_event(event_data, private_key_b64)
    
    event = Event(
        event_hash=event_hash,
        object_id=object_id,
        event_type=event_type,
        prev_event_hash=None,
        timestamp=timestamp_utc,
        actor_id=actor_id,
        payload_json=json.dumps(payload),
        signature_b64=signature
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def append_event(
    db: Session,
    object_id: str,
    event_type: str,
    payload: dict,
    actor_id: str,
    private_key_b64: str
) -> Event:
    """
    Append new event to chain, linking to previous event.
    """
    # Verify object exists
    obj = db.query(Object).filter(Object.object_id == object_id).first()
    if not obj:
        raise ValueError(f"Object {object_id} not found")
    
    # Get previous event
    prev_event = get_latest_event(db, object_id)
    prev_event_hash = prev_event.event_hash if prev_event else None
    
    # Get a single timestamp and use it for both signing and storing
    # This ensures the stored timestamp matches exactly what was signed
    from datetime import timezone
    timestamp_utc = datetime.now(timezone.utc)
    
    # Convert to timezone-naive UTC for signing (matches datetime.utcnow() behavior)
    # This ensures consistent canonical JSON representation
    timestamp_for_signing = timestamp_utc.replace(tzinfo=None).isoformat()
    
    event_data = {
        "object_id": object_id,
        "event_type": event_type,
        "prev_event_hash": prev_event_hash,
        "timestamp": timestamp_for_signing,
        "actor_id": actor_id,
        "payload": payload
    }
    
    event_hash = hash_event(event_data)
    signature = sign_event(event_data, private_key_b64)
    
    event = Event(
        event_hash=event_hash,
        object_id=object_id,
        event_type=event_type,
        prev_event_hash=prev_event_hash,
        timestamp=timestamp_utc,
        actor_id=actor_id,
        payload_json=json.dumps(payload),
        signature_b64=signature
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

