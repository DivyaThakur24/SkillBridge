"""
Authentication routes for SkillBridge API.

Handles user registration, login, and monitoring officer token generation.
All users can sign up with any role, but login credentials must be valid
and monitoring tokens require both JWT and API key validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database import get_db
from src.models import User, RoleEnum
from src.schemas import UserCreate, TokenResponse, MonitoringTokenRequest, MonitoringTokenResponse
from src.auth import hash_password, verify_password, create_access_token, create_monitoring_token, extract_user_id_and_role, decode_token
from src.config import settings
from typing import Optional

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Request body for login endpoint."""
    email: str
    password: str


@router.post("/signup", response_model=TokenResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Sign up a new user and return JWT token.
    
    Creates a new user account with the provided name, email, password, and role.
    Password is hashed with bcrypt before storage. A JWT token is immediately
    returned for convenience.
    
    Args:
        user_data: Signup data including name, email, password, role
        db: Database session
        
    Returns:
        TokenResponse: JWT access token
        
    Raises:
        HTTPException: 400 if email already registered
        
    Example Request:
        {
            "name": "John Student",
            "email": "john@example.com",
            "password": "securepass123",
            "role": "student"
        }
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password before storing
    hashed_password = hash_password(user_data.password)
    
    # Create new user record
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        institution_id=user_data.institution_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate JWT token with user claims
    token = create_access_token({
        "user_id": db_user.id,
        "role": db_user.role.value,
        "email": db_user.email
    })
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Log in a user and return JWT token.
    
    Validates email and password, then returns a JWT token if credentials are correct.
    Token can be used to authenticate subsequent requests.
    
    Args:
        login_data: Email and password credentials
        db: Database session
        
    Returns:
        TokenResponse: JWT access token valid for 24 hours
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password hash matches
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate JWT token with user claims
    token = create_access_token({
        "user_id": user.id,
        "role": user.role.value,
        "email": user.email
    })
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/monitoring-token", response_model=MonitoringTokenResponse)
def get_monitoring_token(
    request: MonitoringTokenRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get a monitoring-scoped token for Monitoring Officer access.
    
    Implements dual-layer authentication for Monitoring Officer role:
    1. API key validation (passed in request body)
    2. Existing JWT validation (passed in Authorization header)
    
    Returns a short-lived (1 hour) monitoring token scoped only to
    read-only monitoring endpoints.
    
    Args:
        request: MonitoringTokenRequest with API key
        authorization: Bearer token from Authorization header
        db: Database session
        
    Returns:
        MonitoringTokenResponse: Monitoring-scoped JWT token (1 hour expiry)
        
    Raises:
        HTTPException: 401 if API key or JWT is invalid
        HTTPException: 401 if user is not a monitoring officer
        
    Security Flow:
        1. Client provides monitoring_officer JWT + API key
        2. We validate API key matches MONITORING_OFFICER_API_KEY
        3. We validate JWT is valid and user is monitoring_officer role
        4. We return a new token scoped to "monitoring" with 1-hour expiry
        5. Client uses this token to access /monitoring/attendance endpoint
    """
    # Step 1: Validate API key
    if request.key != settings.MONITORING_OFFICER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Step 2: Extract and validate Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    # Extract token from "Bearer <token>" format
    token = authorization[7:]
    
    # Step 3: Decode token and verify it's for a monitoring officer
    user_id, role = extract_user_id_and_role(token)
    if user_id is None or role != RoleEnum.MONITORING_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or not a monitoring officer"
        )
    
    # Step 4: Generate scoped monitoring token
    monitoring_token = create_monitoring_token(user_id, role)
    return {"monitoring_token": monitoring_token, "token_type": "bearer"}
