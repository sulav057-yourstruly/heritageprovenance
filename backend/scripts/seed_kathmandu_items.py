"""
Seed 1-2 Kathmandu heritage items into the public gallery.

This is intentionally small and uses locally available placeholder images from data/binaries/.
Replace these images later with real, properly-sourced media.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.db import SessionLocal, init_db
from app.models import Object, Actor
from app.crypto import compute_cid, derive_keypair_from_seed
from app.provenance import create_genesis_event
from app.utils import save_photo, OBJECTS_DIR


BASE_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = BASE_DIR / "data" / "binaries"


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Use a deterministic actor for seeding (institutional authority)
        actor_id = "admin-seed"
        actor = db.query(Actor).filter(Actor.actor_id == actor_id).first()
        if not actor:
            _, pub = derive_keypair_from_seed(f"actor:{actor_id}")
            actor = Actor(actor_id=actor_id, name="Archive Admin (Seed)", pubkey_ed25519=pub)
            db.add(actor)
            db.commit()

        priv, _pub = derive_keypair_from_seed(f"actor:{actor_id}")

        # Choose 2 placeholder images that exist in this repo
        img1 = BIN_DIR / "48e85c05-140c-462e-b761-e420228a5b4e_gwoc.jpg"
        img2 = BIN_DIR / "a9aef7b5-6fde-4128-ab13-8660c5600d7b_unnamed.jpg"
        if not img1.exists():
            img1 = next(BIN_DIR.glob("*.jpg"))
        if not img2.exists():
            img2 = next(BIN_DIR.glob("*.png"))

        items = [
            {
                "title": "Swayambhunath Stupa — Early 20th Century Photograph (Placeholder)",
                "description": (
                    "A placeholder record representing an archival photograph of Swayambhunath Stupa. "
                    "Replace this media with a properly-sourced historical photograph and update references. "
                    "Swayambhunath is among the oldest sacred sites in the Kathmandu Valley and a key locus "
                    "of Newar and wider Himalayan Buddhist practice."
                ),
                "heritage_type": "photograph",
                "location": "Swayambhunath, Kathmandu (Kathmandu Valley)",
                "date_created": "c. 1920 (placeholder)",
                "culture": "Buddhist, Newar",
                "significance": (
                    "Archival images provide comparative evidence for conservation history and changing urban contexts. "
                    "This record is meant to demonstrate the archive's provenance + verification workflow."
                ),
                "keywords": ["swayambhunath", "stupa", "kathmandu", "archive", "photograph"],
                "references": [
                    "UNESCO World Heritage Centre. Kathmandu Valley documentation (placeholder citation).",
                    "Replace with a specific catalogue reference or publication.",
                ],
                "primary_path": img1,
            },
            {
                "title": "Milarepa Thangka Painting — Patan Museum (Placeholder)",
                "description": (
                    "A placeholder record representing a thangka depicting Milarepa. "
                    "Replace this media with a properly-sourced image and catalogue metadata. "
                    "Thangka paintings reflect devotional, pedagogical, and artistic traditions in the Kathmandu Valley "
                    "and broader Himalayan Buddhism."
                ),
                "heritage_type": "artwork",
                "location": "Patan Museum, Lalitpur (Kathmandu Valley)",
                "date_created": "17th century (placeholder)",
                "culture": "Tibetan Buddhist, Newar tradition",
                "significance": (
                    "Demonstrates the archive's emphasis on cultural context, citations, and provenance integrity. "
                    "This placeholder record should be replaced with institutionally-verified catalogue data."
                ),
                "keywords": ["milarepa", "thangka", "patan", "newar", "buddhism"],
                "references": [
                    "Lhalungpa, Lobsang P. The Life of Milarepa (placeholder citation).",
                    "Replace with Patan Museum catalogue entry and image credit.",
                ],
                "primary_path": img2,
            },
        ]

        created = 0
        for it in items:
            content = _read_bytes(it["primary_path"])
            cid = compute_cid(content)

            # Avoid duplicates by CID
            existing = db.query(Object).filter(Object.cid_sha256 == cid).first()
            if existing:
                continue

            saved_path = save_photo(content, OBJECTS_DIR, it["primary_path"].name)
            object_id = str(uuid.uuid4())

            obj = Object(
                object_id=object_id,
                cid_sha256=cid,
                bundle_manifest_json=json.dumps(
                    {
                        "title": it["title"],
                        "description": it["description"],
                        "seeded": True,
                    }
                ),
                title=it["title"],
                description=it["description"],
                heritage_type=it["heritage_type"],
                location=it["location"],
                date_created=it["date_created"],
                culture=it["culture"],
                significance=it["significance"],
                keywords_json=json.dumps(it["keywords"]),
                references_json=json.dumps(it["references"]),
                primary_photo_path=saved_path,
                related_photos_json=None,
                owner_id=None,
                visibility="public",
                published_at=datetime.now(timezone.utc),
                published_by=None,
            )
            db.add(obj)
            db.commit()

            create_genesis_event(
                db=db,
                object_id=object_id,
                event_type="INGESTION",
                payload={
                    "cid": cid,
                    "title": it["title"],
                    "note": "Seeded public heritage item (placeholder media).",
                },
                actor_id=actor_id,
                private_key_b64=priv,
            )

            created += 1

        print(f"[OK] Seed complete. Created {created} public item(s).")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

