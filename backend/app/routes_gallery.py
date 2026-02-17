"""
Public gallery routes (no authentication required).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db import get_db
from app.models import Object
from app.schemas import ItemSummary, ItemDetail
import json

router = APIRouter(prefix="/gallery", tags=["gallery"])

@router.get("", response_model=List[ItemSummary])
async def list_items(
    q: Optional[str] = Query(None, description="Search query"),
    heritage_type: Optional[str] = Query(None, description="Filter by heritage type"),
    culture: Optional[str] = Query(None, description="Filter by culture"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: Session = Depends(get_db)
):
    """List all public items with optional search and filters."""
    query = db.query(Object).filter(Object.visibility == 'public')
    
    # Search
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Object.title.ilike(search_term),
                Object.description.ilike(search_term),
                Object.location.ilike(search_term),
                Object.culture.ilike(search_term),
                Object.keywords_json.ilike(search_term)
            )
        )
    
    # Filters
    if heritage_type:
        query = query.filter(Object.heritage_type == heritage_type)
    if culture:
        query = query.filter(Object.culture == culture)
    if location:
        query = query.filter(Object.location.ilike(f"%{location}%"))
    
    items = query.order_by(Object.published_at.desc()).all()
    
    return [
        ItemSummary(
            object_id=item.object_id,
            title=item.title or "Untitled",
            heritage_type=item.heritage_type,
            location=item.location,
            culture=item.culture,
            primary_photo_path=item.primary_photo_path,
            date_created=item.date_created
        )
        for item in items
    ]

@router.get("/search", response_model=List[ItemSummary])
async def search_items(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db)
):
    """Search items by title, keywords, location."""
    return await list_items(q=q, db=db)

@router.get("/items/{object_id}", response_model=ItemDetail)
async def get_item(object_id: str, db: Session = Depends(get_db)):
    """Get item details with all photos."""
    item = db.query(Object).filter(Object.object_id == object_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Parse JSON fields
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
