from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.models import User, Session as SessionModel, Batch, BatchStudent, Attendance, RoleEnum, AttendanceStatus
from src.schemas import SessionCreate, SessionResponse, AttendanceMarkRequest, AttendanceResponse
from src.auth import extract_user_id_and_role

router = APIRouter(tags=["sessions", "attendance"])


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
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


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    session_data: SessionCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new session (Trainer only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.TRAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can create sessions"
        )
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == session_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verify trainer is associated with this batch
    is_associated = db.query(User).filter(
        User.id == current_user.id,
        User.batches_as_trainer.any(Batch.id == session_data.batch_id)
    ).first()
    
    if not is_associated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trainer is not associated with this batch"
        )
    
    # Validate time format
    try:
        start_parts = session_data.start_time.split(":")
        end_parts = session_data.end_time.split(":")
        if len(start_parts) != 2 or len(end_parts) != 2:
            raise ValueError()
        int(start_parts[0]), int(start_parts[1])
        int(end_parts[0]), int(end_parts[1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid time format. Use HH:MM"
        )
    
    # Create session
    db_session = SessionModel(
        batch_id=session_data.batch_id,
        trainer_id=current_user.id,
        title=session_data.title,
        date=session_data.date,
        start_time=session_data.start_time,
        end_time=session_data.end_time
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session


@router.get("/sessions/{session_id}/attendance")
def get_session_attendance(
    session_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get attendance list for a session (Trainer only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.TRAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can view session attendance"
        )
    
    # Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify trainer is the creator of this session
    if session.trainer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view attendance for your own sessions"
        )
    
    # Get attendance records
    attendance_records = db.query(Attendance).filter(
        Attendance.session_id == session_id
    ).all()
    
    attendance_list = []
    for record in attendance_records:
        student = db.query(User).filter(User.id == record.student_id).first()
        attendance_list.append({
            "student_id": record.student_id,
            "student_name": student.name if student else "Unknown",
            "status": record.status.value
        })
    
    return {
        "session_id": session_id,
        "title": session.title,
        "date": session.date,
        "attendance": attendance_list
    }


@router.post("/attendance/mark", response_model=AttendanceResponse)
def mark_attendance(
    request: AttendanceMarkRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Mark attendance for a session (Student only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can mark attendance"
        )
    
    # Verify session exists
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if student is enrolled in the batch
    is_enrolled = db.query(BatchStudent).filter(
        BatchStudent.batch_id == session.batch_id,
        BatchStudent.student_id == current_user.id
    ).first()
    
    if not is_enrolled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not enrolled in this batch"
        )
    
    # Check if already marked
    existing = db.query(Attendance).filter(
        Attendance.session_id == request.session_id,
        Attendance.student_id == current_user.id
    ).first()
    
    if existing:
        # Update existing record
        existing.status = request.status
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create attendance record
    db_attendance = Attendance(
        session_id=request.session_id,
        student_id=current_user.id,
        status=request.status
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    return db_attendance
