"""JWT Token encoding, decoding, and password hashing utility."""
import hashlib
import datetime
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

from src.config import settings
from src.utils.logger import logger

# Password context with bcrypt and fallback
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashes plain password using bcrypt (with SHA-256 fallback if bcrypt has environment limitations)."""
    try:
        return pwd_context.hash(password)
    except Exception:
        # Robust fallback for environments where native bcrypt libraries differ
        salt = settings.JWT_SECRET_KEY[:8]
        return f"sha256${hashlib.sha256((password + salt).encode('utf-8')).hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored hash."""
    if not hashed_password:
        return False
    if hashed_password.startswith("sha256$"):
        salt = settings.JWT_SECRET_KEY[:8]
        expected = f"sha256${hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()}"
        return expected == hashed_password
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Encodes JWT access token with expiration and user payload."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.datetime.now(datetime.timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token; returns None if invalid or expired."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT Token validation error: {e}")
        return None
