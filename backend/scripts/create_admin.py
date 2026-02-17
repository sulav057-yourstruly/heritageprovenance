"""
Create admin user for Kathmandu Cultural Heritage Archive.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
from datetime import datetime, timezone
from app.db import SessionLocal, init_db
from app.models import User
from app.security import hash_password

def create_admin():
    """Create admin user."""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        admin_email = "admin@kathmandu-heritage.np"
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print(f"[ERROR] Admin user already exists: {admin_email}")
            return
        
        # Create admin
        admin_password = "change-on-first-login"
        admin = User(
            user_id=str(uuid.uuid4()),
            email=admin_email,
            password_hash=hash_password(admin_password),
            name="Heritage Archive Administrator",
            role="admin",
            status="active",
            approved_at=datetime.now(timezone.utc)
        )
        
        db.add(admin)
        db.commit()
        
        print("[OK] Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
