"""
Authentication and authorization utilities.
"""
import os
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

security = HTTPBearer(auto_error=False)

def create_access_token(user_id: str, role: str) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        # Any JWT error -> treat as invalid/expired
        return None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token. Returns None if no token (for public access)."""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or user.status != 'active':
        return None
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    return user

async def require_contributor(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require contributor or admin role."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    if user.role not in ['contributor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contributor access required"
        )
    return user

async def require_admin(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require admin role."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
