"""
API route handlers.
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
import datetime as dt
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Actor, Object, Event, AnchorProof
from app.schemas import (
    ActorCreate, ActorResponse,
    IngestResponse,
    EventCreate, EventResponse,
    AnchorResponse,
    VerificationReport, EventTimelineItem
)
from app.crypto import compute_cid, generate_keypair
from app.provenance import create_genesis_event, append_event, get_latest_event
from app.merkle import merkle_proof, verify_merkle_proof
from app.anchor import anchor_batch, get_all_anchors

router = APIRouter()

# Binary storage directory
BINARY_DIR = Path(__file__).parent.parent / "data" / "binaries"
BINARY_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/actors", response_model=ActorResponse)
async def create_actor(actor_data: ActorCreate, db: Session = Depends(get_db)):
    """Create/register an actor (institution/curator) with public key."""
    # Check if actor already exists
    existing = db.query(Actor).filter(Actor.actor_id == actor_data.actor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Actor ID already exists")
    
    # If no public key provided, derive one deterministically from actor_id
    # This ensures consistency - same actor_id always gets same keypair
    if not actor_data.pubkey_ed25519:
        from app.crypto import derive_keypair_from_seed
        _, pub_key = derive_keypair_from_seed(f"actor:{actor_data.actor_id}")
        actor_data.pubkey_ed25519 = pub_key
    
    actor = Actor(
        actor_id=actor_data.actor_id,
        name=actor_data.name,
        pubkey_ed25519=actor_data.pubkey_ed25519
    )
    db.add(actor)
    db.commit()
    db.refresh(actor)
    return actor

@router.post("/actors/generate", response_model=dict)
async def generate_actor_keypair():
    """Generate a new Ed25519 keypair for an actor."""
    priv_key, pub_key = generate_keypair()
    return {
        "private_key": priv_key,
        "public_key": pub_key,
        "note": "Store the private key securely. Use the public key when creating an actor."
    }

@router.post("/ingest", response_model=IngestResponse)
async def ingest_object(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    actor_id: str = Form(...),
    private_key: str = Form(None),  # MVP: accept private key as form field
    db: Session = Depends(get_db)
):
    """Ingest a digital heritage object: upload file, generate CID, create genesis event."""
    # Verify actor exists
    actor = db.query(Actor).filter(Actor.actor_id == actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    
    # MVP: Always derive private key deterministically from actor_id
    # This ensures the same actor always uses the same keypair for signing
    from app.crypto import derive_keypair_from_seed
    derived_private_key, derived_pub_key = derive_keypair_from_seed(f"actor:{actor_id}")
    
    # Use provided private key if given, otherwise use derived one
    if not private_key:
        private_key = derived_private_key
    
    # Ensure actor's public key matches the derived one (important for verification)
    if actor.pubkey_ed25519 != derived_pub_key:
        actor.pubkey_ed25519 = derived_pub_key
        db.commit()
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Compute CID
    cid = compute_cid(file_bytes)
    
    # Check if object with this CID already exists
    existing_obj = db.query(Object).filter(Object.cid_sha256 == cid).first()
    if existing_obj:
        raise HTTPException(status_code=400, detail="Object with this CID already exists")
    
    # Generate object_id
    object_id = str(uuid.uuid4())
    
    # Parse metadata
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        metadata_dict = {}
    
    # Create bundle manifest
    bundle_manifest = {
        "object_id": object_id,
        "cid": cid,
        "filename": file.filename,
        "content_type": file.content_type,
        "metadata": metadata_dict,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store binary file
    binary_path = BINARY_DIR / f"{object_id}_{file.filename}"
    with open(binary_path, "wb") as f:
        f.write(file_bytes)
    
    # Create object record
    obj = Object(
        object_id=object_id,
        cid_sha256=cid,
        bundle_manifest_json=json.dumps(bundle_manifest)
    )
    db.add(obj)
    db.commit()
    
    # Create genesis event
    genesis_event = create_genesis_event(
        db=db,
        object_id=object_id,
        event_type="INGESTION",
        payload={
            "cid": cid,
            "filename": file.filename,
            "metadata": metadata_dict
        },
        actor_id=actor_id,
        private_key_b64=private_key
    )
    
    return IngestResponse(
        object_id=object_id,
        cid=cid,
        genesis_event_hash=genesis_event.event_hash
    )

@router.post("/objects/{object_id}/events", response_model=EventResponse)
async def create_event(
    object_id: str,
    event_data: EventCreate,
    private_key: str = Query(None, description="Private key for signing (MVP: optional, will auto-generate if missing)"),
    db: Session = Depends(get_db)
):
    """Append a new event to an object's provenance chain. Visitors can create events using 'anonymous' actor_id."""
    
    # Verify object exists
    obj = db.query(Object).filter(Object.object_id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # If actor_id is 'anonymous' or not provided, use anonymous actor for visitors
    actor_id = event_data.actor_id if event_data.actor_id else "anonymous"
    
    # Get or create actor
    actor = db.query(Actor).filter(Actor.actor_id == actor_id).first()
    if not actor:
        # Create anonymous actor for visitor events
        from app.crypto import derive_keypair_from_seed
        _, pub_key = derive_keypair_from_seed(f"actor:{actor_id}")
        actor = Actor(
            actor_id=actor_id,
            name="Anonymous Visitor" if actor_id == "anonymous" else actor_id,
            pubkey_ed25519=pub_key
        )
        db.add(actor)
        db.commit()
    
    # MVP: Always derive private key deterministically from actor_id
    # This ensures the same actor always uses the same keypair for signing
    # The actor's stored public key should match this derived one
    from app.crypto import derive_keypair_from_seed
    derived_private_key, derived_pub_key = derive_keypair_from_seed(f"actor:{actor_id}")
    
    # Use provided private key if given, otherwise use derived one
    if not private_key:
        private_key = derived_private_key
    
    # Ensure actor's public key matches the derived one
    if actor.pubkey_ed25519 != derived_pub_key:
        actor.pubkey_ed25519 = derived_pub_key
        db.commit()
    
    # Append event
    event = append_event(
        db=db,
        object_id=object_id,
        event_type=event_data.event_type,
        payload=event_data.payload,
        actor_id=actor_id,
        private_key_b64=private_key
    )
    
    return EventResponse(event_hash=event.event_hash)

@router.post("/anchor", response_model=AnchorResponse)
async def anchor_events(db: Session = Depends(get_db)):
    """Anchor unanchored events by computing Merkle root and storing it."""
    # Get all events that don't have anchor proofs
    anchored_events = db.query(AnchorProof.event_hash).subquery()
    unanchored_events = db.query(Event).filter(
        ~Event.event_hash.in_(db.query(AnchorProof.event_hash))
    ).all()
    
    if not unanchored_events:
        raise HTTPException(status_code=400, detail="No unanchored events to anchor")
    
    event_hashes = [e.event_hash for e in unanchored_events]
    
    # Compute Merkle root and anchor
    anchor_record = anchor_batch(event_hashes)
    
    # Generate inclusion proofs and store them
    from app.merkle import merkle_proof
    
    root, proof_path = merkle_proof(event_hashes[0], event_hashes)  # Proof for first event as example
    # In practice, we'd generate proofs for all events
    
    for event_hash in event_hashes:
        # Generate proof for each event
        root_check, proof = merkle_proof(event_hash, event_hashes)
        assert root_check == anchor_record["merkle_root"]
        
        proof_record = AnchorProof(
            event_hash=event_hash,
            batch_id=anchor_record["batch_id"],
            merkle_root=anchor_record["merkle_root"],
            proof_path=json.dumps(proof),
            anchored_at=datetime.fromisoformat(anchor_record["anchored_at"].replace('Z', '+00:00'))
        )
        db.add(proof_record)
    
    db.commit()
    
    return AnchorResponse(
        batch_id=anchor_record["batch_id"],
        merkle_root=anchor_record["merkle_root"],
        anchored_at=datetime.fromisoformat(anchor_record["anchored_at"].replace('Z', '+00:00')),
        event_count=anchor_record["event_count"]
    )

@router.post("/verify", response_model=VerificationReport)
async def verify_object(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Verify a file: recompute CID, validate chain, check signatures, verify anchoring."""
    # Read file bytes
    file_bytes = await file.read()
    
    # Compute CID
    cid = compute_cid(file_bytes)
    
    # Find object by CID
    obj = db.query(Object).filter(Object.cid_sha256 == cid).first()
    
    errors = []
    cid_match = obj is not None
    if not cid_match:
        errors.append(f"CID mismatch: file CID {cid} not found in database")
        return VerificationReport(
            cid_match=False,
            chain_valid=False,
            signatures_valid=False,
            anchored=False,
            timeline=[],
            errors=errors
        )
    
    # Get all events for this object, ordered by timestamp
    events = db.query(Event).filter(
        Event.object_id == obj.object_id
    ).order_by(Event.timestamp.asc()).all()
    
    if not events:
        errors.append("No events found for object")
        return VerificationReport(
            cid_match=True,
            chain_valid=False,
            signatures_valid=False,
            anchored=False,
            timeline=[],
            errors=errors
        )
    
    # Validate chain integrity
    chain_valid = True
    signatures_valid = True
    timeline_items = []
    
    for i, event in enumerate(events):
        # Reconstruct event data for verification
        # Parse payload JSON
        try:
            payload = json.loads(event.payload_json)
        except:
            payload = {}
        
        # Reconstruct timestamp in the same format used for signing
        # When creating events, we use: timestamp_utc.replace(tzinfo=None).isoformat()
        # The database stores it as timezone-aware UTC, so we need to convert back to naive UTC
        import datetime as dt
        timestamp_dt = event.timestamp
        if timestamp_dt.tzinfo is not None:
            # Convert to UTC and make it naive (no timezone) to match signing format
            # This matches: timestamp_utc.replace(tzinfo=None).isoformat()
            timestamp_dt = timestamp_dt.astimezone(dt.timezone.utc).replace(tzinfo=None)
        
        # Format exactly as .isoformat() would (timezone-naive)
        timestamp_str = timestamp_dt.isoformat()
        
        event_data = {
            "object_id": event.object_id,
            "event_type": event.event_type,
            "prev_event_hash": event.prev_event_hash,
            "timestamp": timestamp_str,
            "actor_id": event.actor_id,
            "payload": payload
        }
        
        # Verify prev_event_hash link
        if i == 0:
            if event.prev_event_hash is not None:
                chain_valid = False
                errors.append(f"Genesis event {event.event_hash} should have null prev_event_hash")
        else:
            prev_event = events[i-1]
            if event.prev_event_hash != prev_event.event_hash:
                chain_valid = False
                errors.append(f"Event {event.event_hash} has incorrect prev_event_hash")
        
        # Verify signature
        sig_valid = False
        actor = db.query(Actor).filter(Actor.actor_id == event.actor_id).first()
        if actor:
            from app.crypto import verify_signature, derive_keypair_from_seed
            # Always use the derived public key (same as what was used for signing)
            _, derived_pub_key = derive_keypair_from_seed(f"actor:{event.actor_id}")
            
            # Use derived public key for verification (should match what was used for signing)
            sig_valid = verify_signature(event_data, event.signature_b64, derived_pub_key)
            
            if not sig_valid:
                # If derived key doesn't work, try stored key (for backward compatibility)
                if actor.pubkey_ed25519 != derived_pub_key:
                    sig_valid = verify_signature(event_data, event.signature_b64, actor.pubkey_ed25519)
                    if sig_valid:
                        # Update actor's public key to match derived one for future consistency
                        actor.pubkey_ed25519 = derived_pub_key
                        db.commit()
            
            if not sig_valid:
                signatures_valid = False
                errors.append(f"Invalid signature for event {event.event_hash}")
        else:
            signatures_valid = False
            errors.append(f"Actor {event.actor_id} not found for event {event.event_hash}")
        
        # Check if anchored
        anchor_proof = db.query(AnchorProof).filter(AnchorProof.event_hash == event.event_hash).first()
        anchored = anchor_proof is not None
        batch_id = anchor_proof.batch_id if anchor_proof else None
        
        timeline_items.append(EventTimelineItem(
            event_hash=event.event_hash,
            event_type=event.event_type,
            timestamp=event.timestamp,
            actor_id=event.actor_id,
            payload=payload,
            prev_event_hash=event.prev_event_hash,
            signature_valid=sig_valid,
            anchored=anchored,
            batch_id=batch_id
        ))
    
    # Check if any event is anchored
    anchored = any(item.anchored for item in timeline_items)
    
    return VerificationReport(
        cid_match=cid_match,
        chain_valid=chain_valid,
        signatures_valid=signatures_valid,
        anchored=anchored,
        timeline=timeline_items,
        errors=errors
    )

@router.get("/objects/{object_id}/export.jsonld")
async def export_jsonld(object_id: str, db: Session = Depends(get_db)):
    """Export object and provenance events as JSON-LD."""
    from fastapi.responses import JSONResponse
    
    # Get object
    obj = db.query(Object).filter(Object.object_id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # Get all events
    events = db.query(Event).filter(
        Event.object_id == object_id
    ).order_by(Event.timestamp.asc()).all()
    
    # Parse bundle manifest
    try:
        bundle_manifest = json.loads(obj.bundle_manifest_json)
    except:
        bundle_manifest = {}
    
    # Build JSON-LD structure
    jsonld = {
        "@context": {
            "@version": 1.1,
            "dc": "http://purl.org/dc/elements/1.1/",
            "premis": "http://www.loc.gov/premis/rdf/v1#",
            "prov": "http://www.w3.org/ns/prov#",
            "provenance": "urn:provenance:"
        },
        "@id": f"urn:object:{object_id}",
        "@type": "premis:Object",
        "dc:identifier": object_id,
        "provenance:cid": obj.cid_sha256,
        "dc:created": obj.created_at.isoformat(),
        "premis:objectCharacteristics": bundle_manifest.get("metadata", {}),
        "prov:wasGeneratedBy": []
    }
    
    # Add events as provenance activities
    for event in events:
        try:
            payload = json.loads(event.payload_json)
        except:
            payload = {}
        
        event_node = {
            "@id": f"urn:provenance:event:{event.event_hash}",
            "@type": f"provenance:{event.event_type}",
            "prov:atTime": event.timestamp.isoformat(),
            "prov:wasAttributedTo": {
                "@id": f"urn:actor:{event.actor_id}",
                "provenance:actorId": event.actor_id
            },
            "provenance:signature": event.signature_b64,
            "provenance:payload": payload
        }
        
        if event.prev_event_hash:
            event_node["prov:wasInformedBy"] = {
                "@id": f"urn:provenance:event:{event.prev_event_hash}"
            }
        
        jsonld["prov:wasGeneratedBy"].append(event_node)
    
    return JSONResponse(content=jsonld, media_type="application/ld+json")

