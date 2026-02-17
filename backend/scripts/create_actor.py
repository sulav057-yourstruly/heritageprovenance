"""
Helper script to create an actor for testing.
Usage: python scripts/create_actor.py <actor_id> <name>
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db import SessionLocal, init_db
from app.models import Actor
from app.crypto import generate_keypair

def create_actor(actor_id: str, name: str):
    """Create an actor with auto-generated keypair."""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if actor exists
        existing = db.query(Actor).filter(Actor.actor_id == actor_id).first()
        if existing:
            print(f"Actor {actor_id} already exists")
            print(f"Public Key: {existing.pubkey_ed25519}")
            return
        
        # Generate keypair
        private_key, public_key = generate_keypair()
        
        # Create actor
        actor = Actor(
            actor_id=actor_id,
            name=name,
            pubkey_ed25519=public_key
        )
        db.add(actor)
        db.commit()
        
        print(f"Actor created successfully!")
        print(f"Actor ID: {actor_id}")
        print(f"Name: {name}")
        print(f"Public Key: {public_key}")
        print(f"\nPrivate Key (store securely): {private_key}")
        print("\nNote: For MVP, you can use this private key when creating events.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_actor.py <actor_id> <name>")
        sys.exit(1)
    
    actor_id = sys.argv[1]
    name = sys.argv[2]
    create_actor(actor_id, name)

