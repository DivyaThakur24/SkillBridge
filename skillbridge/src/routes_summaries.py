from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from src.database import get_db
from src.models import User, Batch, Institution, Attendance, RoleEnum, AttendanceStatus
from src.auth import extract_user_id_and_role, decode_token

router = APIRouter(tags=["summaries", "monitoring"])


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


@router.get("/institutions/{institution_id}/summary")
def get_institution_summary(
    institution_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get attendance summary across all batches in an institution (Programme Manager only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.PROGRAMME_MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only programme managers can view institution summaries"
        )
    
    # Verify institution exists
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found"
        )
    
    # Get all batches in institution
    batches = db.query(Batch).filter(Batch.institution_id == institution_id).all()
    
    total_batches = len(batches)
    total_students = 0
    total_present = 0
    total_possible = 0
    
    for batch in batches:
        from src.models import BatchStudent
        batch_students = db.query(BatchStudent).filter(BatchStudent.batch_id == batch.id).count()
        total_students += batch_students
        
        # Get attendance for this batch
        attendance = db.query(Attendance).join(
            Attendance.session
        ).filter(
            Attendance.session.has(batch_id=batch.id)
        ).all()
        
        for record in attendance:
            total_possible += 1
            if record.status == AttendanceStatus.PRESENT:
                total_present += 1
    
    average_attendance_rate = (total_present / total_possible * 100) if total_possible > 0 else 0
    
    return {
        "institution_id": institution_id,
        "institution_name": institution.name,
        "total_batches": total_batches,
        "total_students": total_students,
        "average_attendance_rate": round(average_attendance_rate, 2)
    }


@router.get("/programme/summary")
def get_programme_summary(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get programme-wide attendance summary (Programme Manager only)."""
    current_user = get_current_user(authorization, db)
    
    # Check authorization
    if current_user.role != RoleEnum.PROGRAMME_MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only programme managers can view programme summaries"
        )
    
    # Get all institutions
    institutions = db.query(Institution).all()
    total_institutions = len(institutions)
    
    # Get all batches
    total_batches = db.query(Batch).count()
    
    # Get all students
    from src.models import BatchStudent
    total_students = db.query(BatchStudent).distinct(BatchStudent.student_id).count()
    
    # Get overall attendance rate
    all_attendance = db.query(Attendance).all()
    total_present = sum(1 for a in all_attendance if a.status == AttendanceStatus.PRESENT)
    total_possible = len(all_attendance)
    
    overall_attendance_rate = (total_present / total_possible * 100) if total_possible > 0 else 0
    
    return {
        "total_institutions": total_institutions,
        "total_batches": total_batches,
        "total_students": total_students,
        "overall_attendance_rate": round(overall_attendance_rate, 2)
    }


@router.get("/monitoring/attendance")
def get_monitoring_attendance(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get full attendance data across entire programme (Monitoring Officer only)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    token = authorization[7:]
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Check for monitoring scope
    scope = payload.get("scope")
    if scope != "monitoring":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not scoped for monitoring access"
        )
    
    role = payload.get("role")
    if role != "monitoring_officer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not for monitoring officer role"
        )
    
    # Get all attendance records with related info
    attendance_records = db.query(Attendance).all()
    
    result = []
    for record in attendance_records:
        session = db.query(db.query(Attendance).filter(Attendance.id == record.id).first().session).first()
        student = db.query(User).filter(User.id == record.student_id).first()
        
        result.append({
            "attendance_id": record.id,
            "session_id": record.session_id,
            "student_id": record.student_id,
            "student_name": student.name if student else "Unknown",
            "status": record.status.value,
            "marked_at": record.marked_at.isoformat()
        })
    
    return {
        "total_records": len(result),
        "attendance": result
    }


@router.post("/monitoring/attendance")
def post_monitoring_attendance(authorization: Optional[str] = Header(None)):
    """Reject POST requests to monitoring/attendance endpoint."""
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Method Not Allowed"
    )
