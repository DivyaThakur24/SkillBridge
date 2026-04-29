"""
Authentication and JWT utilities for SkillBridge API.

Handles password hashing, JWT token creation/validation, and user authentication.
All passwords are hashed with bcrypt, and JWTs are signed with HS256 algorithm.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.config import settings
from src.models import RoleEnum

# Bcrypt password hashing context
# deprecated="auto" means older password formats will be rehashed on next login
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Bcrypt hashed password string (safe to store in database)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its bcrypt hash.
    
    Args:
        plain_password: User-provided password
        hashed_password: Stored bcrypt hash from database
        
    Returns:
        True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.
    
    Args:
        data: Dictionary of claims to include in JWT (user_id, role, email, etc.)
        expires_delta: Custom token expiry duration (defaults to JWT_EXPIRATION_HOURS)
        
    Returns:
        Encoded JWT token string
        
    Example:
        token = create_access_token({
            "user_id": 123,
            "role": "student",
            "email": "user@example.com"
        })
    """
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    # Add standard JWT claims
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    # Encode JWT using secret key and algorithm from settings
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_monitoring_token(user_id: int, role: RoleEnum) -> str:
    """
    Create a scoped monitoring token for Monitoring Officer role.
    
    This is a special short-lived token with 1-hour expiry used by the
    Monitoring Officer after passing API key validation. It includes
    a "scope" claim set to "monitoring" to identify its purpose.
    
    Args:
        user_id: ID of the monitoring officer user
        role: User's role (must be monitoring_officer)
        
    Returns:
        Encoded JWT monitoring token with 1-hour expiry
    """
    data = {
        "user_id": user_id,
        "role": role,
        "scope": "monitoring"  # Scope field identifies this as a monitoring token
    }
    # Monitoring tokens expire in 1 hour (much shorter than standard 24 hours)
    expires_delta = timedelta(minutes=settings.MONITORING_TOKEN_EXPIRATION_MINUTES)
    return create_access_token(data, expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Dictionary of decoded token claims if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid, expired, or tampered with
        return None


def extract_user_id_and_role(token: str) -> tuple[Optional[int], Optional[RoleEnum]]:
    """
    Extract user ID and role from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Tuple of (user_id, role) if token is valid, (None, None) if invalid
    """
    payload = decode_token(token)
    if payload is None:
        return None, None
    
    user_id = payload.get("user_id")
    role_str = payload.get("role")
    
    # Convert role string back to RoleEnum
    try:
        role = RoleEnum(role_str) if role_str else None
    except ValueError:
        role = None
    
    return user_id, role
