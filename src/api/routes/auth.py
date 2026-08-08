"""Authentication routes: Register, Login, Profile, and Logout."""
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User
from src.auth.jwt_handler import get_password_hash, verify_password, create_access_token
from src.auth.dependencies import get_current_user
from src.api.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
)
from src.utils.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new customer account and returns a JWT access token."""
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user_id = f"user_{uuid.uuid4().hex[:8]}"
    hashed_pwd = get_password_hash(req.password)

    new_user = User(
        id=user_id,
        email=req.email.lower(),
        hashed_password=hashed_pwd,
        name=req.name,
        role="customer",
        status="active",
        created_at=datetime.datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Registered new user: {new_user.email} (ID: {new_user.id})")

    token = create_access_token(data={"sub": new_user.id, "email": new_user.email, "role": new_user.role})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
    )


@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticates credentials and returns a JWT access token."""
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If seeded user without hashed password, allow default password or check hash
    valid = False
    if user.hashed_password:
        valid = verify_password(req.password, user.hashed_password)
    else:
        # Default test password for seeded users
        valid = req.password in ("password123", "secret", "demo123", "password")
        if valid:
            user.hashed_password = get_password_hash(req.password)
            db.commit()

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
    )


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieves authenticated user profile information."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        status=current_user.status,
        created_at=current_user.created_at,
    )


@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    """Logs out the active session."""
    return {"success": True, "message": "Successfully logged out."}
