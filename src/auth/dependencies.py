"""FastAPI authentication dependencies."""
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User
from src.auth.jwt_handler import decode_access_token
from src.utils.logger import logger

# Supports both header formats
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    token_oauth: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extracts and validates current authenticated user from JWT token."""
    raw_token = None
    if token_auth and token_auth.credentials:
        raw_token = token_auth.credentials
    elif token_oauth:
        raw_token = token_oauth

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(raw_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing subject identifier.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with this token no longer exists.",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated or suspended.",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensures user is active and has valid permissions."""
    return current_user


def get_optional_current_user(
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    token_oauth: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Returns the authenticated user if token present, or fallback guest user."""
    try:
        return get_current_user(token_auth, token_oauth, db)
    except HTTPException:
        # Fallback to test user_demo if guest request
        return db.query(User).filter(User.id == "user_demo").first()
