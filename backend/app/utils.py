"""
Utility functions for photo handling and activity logging.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from PIL import Image
from sqlalchemy.orm import Session
from app.models import ActivityLog

# Photo storage directories
BASE_DIR = Path(__file__).parent.parent
OBJECTS_DIR = BASE_DIR / "data" / "objects"
REQUESTS_DIR = BASE_DIR / "data" / "requests"
OBJECTS_DIR.mkdir(parents=True, exist_ok=True)
REQUESTS_DIR.mkdir(parents=True, exist_ok=True)

def save_photo(file_content: bytes, directory: Path, filename: str) -> str:
    """Save photo and generate thumbnails. Returns relative path."""
    photo_dir = directory / filename.split('.')[0]
    photo_dir.mkdir(parents=True, exist_ok=True)
    
    # Save original
    original_path = photo_dir / f"original_{filename}"
    with open(original_path, 'wb') as f:
        f.write(file_content)
    
    # Generate thumbnails
    img = Image.open(original_path)
    
    # Small: 300x300
    img_small = img.copy()
    img_small.thumbnail((300, 300), Image.Resampling.LANCZOS)
    img_small.save(photo_dir / f"small_{filename}", optimize=True, quality=85)
    
    # Medium: 800x800
    img_medium = img.copy()
    img_medium.thumbnail((800, 800), Image.Resampling.LANCZOS)
    img_medium.save(photo_dir / f"medium_{filename}", optimize=True, quality=85)
    
    # Large: 1600x1600
    img_large = img.copy()
    img_large.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    img_large.save(photo_dir / f"large_{filename}", optimize=True, quality=85)
    
    return str(original_path.relative_to(BASE_DIR))

def log_activity(
    db: Session,
    user_id: Optional[str],
    action_type: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None
):
    """Log an activity."""
    log = ActivityLog(
        log_id=str(uuid.uuid4()),
        user_id=user_id,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        details_json=json.dumps(details) if details else None,
        ip_address=ip_address,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(log)
    db.commit()

def get_client_ip(request) -> Optional[str]:
    """Extract client IP from request."""
    if hasattr(request, 'client') and request.client:
        return request.client.host
    return None
