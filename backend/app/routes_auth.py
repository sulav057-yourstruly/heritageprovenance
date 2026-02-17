"""
Authentication routes.
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import LoginRequest, LoginResponse, UserResponse
from app.auth import create_access_token, get_current_user
from app.security import hash_password, verify_password
from app.utils import log_activity, get_client_ip

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login and get JWT token."""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    # Create token
    access_token = create_access_token(user.user_id, user.role)
    
    # Log activity
    log_activity(
        db=db,
        user_id=user.user_id,
        action_type="login",
        ip_address=get_client_ip(request)
    )
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role,
            bio=user.bio,
            affiliation=user.affiliation
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        role=user.role,
        bio=user.bio,
        affiliation=user.affiliation
    )

@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout (client should discard token)."""
    if user:
        log_activity(
            db=db,
            user_id=user.user_id,
            action_type="logout"
        )
    return {"message": "Logged out successfully"}
