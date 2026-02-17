"""
Mock anchoring: store Merkle roots in JSON file.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from app.merkle import merkle_root

ANCHOR_FILE = Path(__file__).parent.parent / "data" / "anchors.json"

def load_anchors() -> List[Dict[str, Any]]:
    """Load anchors from JSON file."""
    if not ANCHOR_FILE.exists():
        return []
    with open(ANCHOR_FILE, 'r') as f:
        return json.load(f)

def save_anchors(anchors: List[Dict[str, Any]]):
    """Save anchors to JSON file."""
    ANCHOR_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ANCHOR_FILE, 'w') as f:
        json.dump(anchors, f, indent=2, default=str)

def anchor_batch(event_hashes: List[str]) -> Dict[str, Any]:
    """
    Anchor a batch of events by computing Merkle root and storing it.
    Returns anchor record with batch_id, merkle_root, anchored_at, event_count.
    """
    if not event_hashes:
        raise ValueError("Cannot anchor empty batch")
    
    merkle_root_hash = merkle_root(event_hashes)
    batch_id = str(uuid.uuid4())
    anchored_at = datetime.utcnow()
    
    anchor_record = {
        "batch_id": batch_id,
        "merkle_root": merkle_root_hash,
        "anchored_at": anchored_at.isoformat(),
        "event_count": len(event_hashes),
        "event_hashes": event_hashes  # Store for proof generation
    }
    
    anchors = load_anchors()
    anchors.append(anchor_record)
    save_anchors(anchors)
    
    return anchor_record

def get_anchor_by_batch_id(batch_id: str) -> Dict[str, Any] | None:
    """Get anchor record by batch_id."""
    anchors = load_anchors()
    for anchor in anchors:
        if anchor["batch_id"] == batch_id:
            return anchor
    return None

def get_all_anchors() -> List[Dict[str, Any]]:
    """Get all anchor records."""
    return load_anchors()

