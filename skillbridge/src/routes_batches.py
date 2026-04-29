"""
Batch management routes for SkillBridge API.

Handles batch creation, invitation, and student enrollment. Batches represent
training cohorts that contain multiple students and are taught by one or more trainers.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from typing import Optional
from src.database import get_db
from src.models import User, Batch, BatchStudent, BatchInvite, RoleEnum, Institution
from src.schemas import BatchCreate, BatchResponse, BatchInviteResponse, BatchJoinRequest
from src.auth import extract_user_id_and_role, decode_token

router = APIRouter(prefix="/batches", tags=["batches"])


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """
    Dependency to extract and validate current user from JWT token.
    
    Args:
        authorization: Authorization header value (Bearer token)
        db: Database session
        
    Returns:
        User object if token is valid
        
    Raises:
        HTTPException: 401 if token missing, invalid, or user not found
    """
    """Extract current user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    token = authorization[7:]
    user_id, role = extract_user_id_and_role(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=BatchResponse)
def create_batch(
    batch_data: BatchCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new batch (Trainer or Institution only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role not in [RoleEnum.TRAINER, RoleEnum.INSTITUTION]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and institutions can create batches"
        )
    
    # Verify institution exists
    institution = db.query(Institution).filter(Institution.id == batch_data.institution_id).first()
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    
    # If trainer, verify they belong to this institution
    if current_user.role == RoleEnum.TRAINER and current_user.institution_id != batch_data.institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trainer can only create batches in their institution"
        )
    
    # Create batch
    db_batch = Batch(
        name=batch_data.name,
        institution_id=batch_data.institution_id
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    
    return db_batch


@router.post("/{batch_id}/invite", response_model=BatchInviteResponse)
def generate_batch_invite(
    batch_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Generate a batch invite token (Trainer only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.TRAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can generate batch invites"
        )
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verify trainer is associated with this batch
    is_associated = db.query(User).filter(
        User.id == current_user.id,
        User.batches_as_trainer.any(Batch.id == batch_id)
    ).first()
    
    if not is_associated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trainer is not associated with this batch"
        )
    
    # Generate invite token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    db_invite = BatchInvite(
        batch_id=batch_id,
        token=token,
        created_by=current_user.id,
        expires_at=expires_at
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    
    return {"token": token, "expires_at": expires_at}


@router.post("/join", response_model=BatchResponse)
def join_batch(
    request: BatchJoinRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Join a batch using an invite token (Student only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can join batches"
        )
    
    # Find invite
    invite = db.query(BatchInvite).filter(BatchInvite.token == request.token).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite token"
        )
    
    # Check if expired
    if invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite token has expired"
        )
    
    # Check if already used
    if invite.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite token has already been used"
        )
    
    # Check if already a member
    existing = db.query(BatchStudent).filter(
        BatchStudent.batch_id == invite.batch_id,
        BatchStudent.student_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already a member of this batch"
        )
    
    # Add student to batch
    db_batch_student = BatchStudent(
        batch_id=invite.batch_id,
        student_id=current_user.id
    )
    db.add(db_batch_student)
    invite.used = True
    db.commit()
    
    # Return batch info
    batch = db.query(Batch).filter(Batch.id == invite.batch_id).first()
    return batch


@router.get("/{batch_id}/summary")
def get_batch_summary(
    batch_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get attendance summary for a batch (Institution only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.INSTITUTION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institutions can view batch summaries"
        )
    
    # Verify batch exists and belongs to this institution
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    if batch.institution_id != current_user.institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view summaries for batches in your institution"
        )
    
    # Calculate summary
    from src.models import Attendance
    
    students = db.query(BatchStudent).filter(BatchStudent.batch_id == batch_id).count()
    sessions = db.query(Attendance).join(
        Attendance.session
    ).filter(
        Attendance.session.has(batch_id=batch_id)
    ).count()
    
    from src.models import AttendanceStatus
    present_count = db.query(Attendance).join(
        Attendance.session
    ).filter(
        Attendance.session.has(batch_id=batch_id),
        Attendance.status == AttendanceStatus.PRESENT
    ).count()
    
    total_possible = students * sessions if sessions > 0 else 1
    attendance_rate = (present_count / total_possible) * 100 if total_possible > 0 else 0
    
    return {
        "batch_id": batch_id,
        "batch_name": batch.name,
        "total_sessions": sessions,
        "total_students": students,
        "attendance_rate": round(attendance_rate, 2)
    }
