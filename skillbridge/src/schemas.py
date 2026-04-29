from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from src.models import RoleEnum, AttendanceStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    institution_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    institution_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MonitoringTokenRequest(BaseModel):
    key: str


class MonitoringTokenResponse(BaseModel):
    monitoring_token: str
    token_type: str = "bearer"


class BatchCreate(BaseModel):
    name: str
    institution_id: int


class BatchResponse(BaseModel):
    id: int
    name: str
    institution_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BatchInviteCreate(BaseModel):
    pass  # Token is generated server-side


class BatchInviteResponse(BaseModel):
    token: str
    expires_at: datetime


class BatchJoinRequest(BaseModel):
    token: str


class SessionCreate(BaseModel):
    batch_id: int
    title: str
    date: datetime
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class SessionResponse(BaseModel):
    id: int
    batch_id: int
    trainer_id: int
    title: str
    date: datetime
    start_time: str
    end_time: str
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceMarkRequest(BaseModel):
    session_id: int
    status: AttendanceStatus


class AttendanceResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    status: AttendanceStatus
    marked_at: datetime

    class Config:
        from_attributes = True


class AttendanceDetailResponse(BaseModel):
    student_id: int
    student_name: str
    status: AttendanceStatus


class SessionAttendanceResponse(BaseModel):
    session_id: int
    title: str
    date: datetime
    attendance: List[AttendanceDetailResponse]


class BatchSummaryResponse(BaseModel):
    batch_id: int
    batch_name: str
    total_sessions: int
    total_students: int
    attendance_rate: float


class InstitutionSummaryResponse(BaseModel):
    institution_id: int
    institution_name: str
    total_batches: int
    total_students: int
    average_attendance_rate: float


class ProgrammeSummaryResponse(BaseModel):
    total_institutions: int
    total_batches: int
    total_students: int
    overall_attendance_rate: float
