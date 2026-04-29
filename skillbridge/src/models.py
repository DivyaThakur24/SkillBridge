"""
Database models (ORM) for SkillBridge attendance management system.

Defines all 8 database tables and their relationships using SQLAlchemy:
- User: System users with roles (Student, Trainer, Institution, etc.)
- Institution: Organizations managing batches and trainers
- Batch: Training cohorts within institutions
- BatchTrainer: Many-to-many relationship between Batches and Trainers
- BatchStudent: Many-to-many relationship between Batches and Students
- BatchInvite: Invite tokens for self-service batch enrollment
- Session: Training sessions within batches
- Attendance: Attendance records for each session
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from src.database import Base


class RoleEnum(str, enum.Enum):
    """
    User role enumeration.
    
    Defines the 5 possible user roles in the system:
    - STUDENT: Can mark attendance, join batches
    - TRAINER: Can create sessions, manage batches, view attendance
    - INSTITUTION: Oversees trainers and batches within their institution
    - PROGRAMME_MANAGER: Views attendance data across all institutions
    - MONITORING_OFFICER: Read-only access to entire programme with dual-token auth
    """
    STUDENT = "student"
    TRAINER = "trainer"
    INSTITUTION = "institution"
    PROGRAMME_MANAGER = "programme_manager"
    MONITORING_OFFICER = "monitoring_officer"


class AttendanceStatus(str, enum.Enum):
    """
    Attendance status enumeration.
    
    Defines the 3 possible attendance statuses when marking attendance:
    - PRESENT: Student was present for the session
    - ABSENT: Student was absent from the session
    - LATE: Student arrived late to the session
    """
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class User(Base):
    """
    User model representing all system users.
    
    Attributes:
        id: Primary key
        name: User's full name
        email: Unique email address (login credential)
        hashed_password: Bcrypt hashed password (never stored plaintext)
        role: User's role in the system (RoleEnum)
        institution_id: Foreign key to Institution (nullable for PM/Monitoring Officer)
        created_at: Timestamp when user was created
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships with other models
    institution = relationship("Institution", back_populates="users")
    batches_as_trainer = relationship("Batch", secondary="batch_trainers", back_populates="trainers")
    sessions = relationship("Session", back_populates="trainer")
    attendance_records = relationship("Attendance", back_populates="student")
    batch_invites_created = relationship("BatchInvite", back_populates="created_by_user")


class Institution(Base):
    """
    Institution model representing organizations in the programme.
    
    Attributes:
        id: Primary key
        name: Institution name
        created_at: Timestamp when institution was created
    """
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="institution")
    batches = relationship("Batch", back_populates="institution")


class Batch(Base):
    """
    Batch model representing training cohorts.
    
    Attributes:
        id: Primary key
        name: Batch name (e.g., "Python Basics Batch 1")
        institution_id: Foreign key to Institution
        created_at: Timestamp when batch was created
    """
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="batches")
    trainers = relationship("User", secondary="batch_trainers", back_populates="batches_as_trainer")
    students = relationship("User", secondary="batch_students")
    sessions = relationship("Session", back_populates="batch")
    invites = relationship("BatchInvite", back_populates="batch")


class BatchTrainer(Base):
    """
    Many-to-many junction table linking Batches and Trainers.
    
    Allows multiple trainers to be assigned to the same batch
    for co-teaching scenarios or coverage.
    
    Attributes:
        batch_id: Foreign key to Batch (primary key)
        trainer_id: Foreign key to User with trainer role (primary key)
    """
    __tablename__ = "batch_trainers"
    
    batch_id = Column(Integer, ForeignKey("batches.id"), primary_key=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class BatchStudent(Base):
    """
    Many-to-many junction table linking Batches and Students.
    
    Records which students are enrolled in which batches.
    
    Attributes:
        batch_id: Foreign key to Batch (primary key)
        student_id: Foreign key to User with student role (primary key)
    """
    __tablename__ = "batch_students"
    
    batch_id = Column(Integer, ForeignKey("batches.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class BatchInvite(Base):
    """
    Batch invite tokens for self-service enrollment.
    
    Trainers generate invite tokens that students can use to join batches.
    This allows asynchronous, self-service batch enrollment without
    requiring trainer/institution admin intervention.
    
    Attributes:
        id: Primary key
        batch_id: Foreign key to Batch
        token: URL-safe 32-character unique invite token
        created_by: Foreign key to User (trainer who created invite)
        expires_at: When the invite token expires (typically 7 days)
        used: Boolean flag to prevent token reuse after first use
    """
    __tablename__ = "batch_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    token = Column(String, unique=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)
    
    # Relationships
    batch = relationship("Batch", back_populates="invites")
    created_by_user = relationship("User", back_populates="batch_invites_created")


class Session(Base):
    """
    Training session model representing individual classes/sessions.
    
    Attributes:
        id: Primary key
        batch_id: Foreign key to Batch
        trainer_id: Foreign key to User (trainer conducting session)
        title: Session title/topic
        date: Date of the session
        start_time: Session start time (format: "HH:MM")
        end_time: Session end time (format: "HH:MM")
        created_at: Timestamp when session was created
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    trainer_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    date = Column(DateTime)
    start_time = Column(String)  # Format: "HH:MM"
    end_time = Column(String)    # Format: "HH:MM"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    batch = relationship("Batch", back_populates="sessions")
    trainer = relationship("User", back_populates="sessions")
    attendance = relationship("Attendance", back_populates="session")


class Attendance(Base):
    """
    Attendance record model tracking who attended which sessions.
    
    Attributes:
        id: Primary key
        session_id: Foreign key to Session
        student_id: Foreign key to User (student marking attendance)
        status: Attendance status (present, absent, late)
        marked_at: Timestamp when attendance was marked
    """
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(AttendanceStatus))
    marked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="attendance")
    student = relationship("User", back_populates="attendance_records")
