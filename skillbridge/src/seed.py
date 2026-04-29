"""
Seed script to populate database with test data.
Usage: python -m src.seed
"""

from datetime import datetime, timedelta
from src.database import SessionLocal, Base, engine
from src.models import (
    User, Institution, Batch, BatchTrainer, BatchStudent, 
    Session as SessionModel, Attendance, BatchInvite, RoleEnum, AttendanceStatus
)
from src.auth import hash_password
import secrets

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Clear existing data (be careful with this in production!)
    db.query(Attendance).delete()
    db.query(SessionModel).delete()
    db.query(BatchInvite).delete()
    db.query(BatchTrainer).delete()
    db.query(BatchStudent).delete()
    db.query(Batch).delete()
    db.query(User).delete()
    db.query(Institution).delete()
    db.commit()
    
    print("Creating institutions...")
    institution1 = Institution(name="Tech Institute", created_at=datetime.utcnow())
    institution2 = Institution(name="Skills Academy", created_at=datetime.utcnow())
    db.add_all([institution1, institution2])
    db.commit()
    db.refresh(institution1)
    db.refresh(institution2)
    print(f"  ✓ Created 2 institutions")
    
    print("Creating users...")
    # Create institution admins
    inst_user1 = User(
        name="Institution Admin 1",
        email="institution1@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.INSTITUTION,
        institution_id=institution1.id
    )
    inst_user2 = User(
        name="Institution Admin 2",
        email="institution2@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.INSTITUTION,
        institution_id=institution2.id
    )
    
    # Create trainers
    trainer1 = User(
        name="Trainer 1",
        email="trainer1@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.TRAINER,
        institution_id=institution1.id
    )
    trainer2 = User(
        name="Trainer 2",
        email="trainer2@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.TRAINER,
        institution_id=institution1.id
    )
    trainer3 = User(
        name="Trainer 3",
        email="trainer3@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.TRAINER,
        institution_id=institution2.id
    )
    trainer4 = User(
        name="Trainer 4",
        email="trainer4@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.TRAINER,
        institution_id=institution2.id
    )
    
    # Create students
    students = []
    for i in range(15):
        student = User(
            name=f"Student {i+1}",
            email=f"student{i+1}@example.com",
            hashed_password=hash_password("password123"),
            role=RoleEnum.STUDENT,
            institution_id=institution1.id if i < 8 else institution2.id
        )
        students.append(student)
    
    # Create programme manager
    prog_manager = User(
        name="Programme Manager",
        email="pm@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.PROGRAMME_MANAGER
    )
    
    # Create monitoring officer
    monitoring = User(
        name="Monitoring Officer",
        email="monitoring@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.MONITORING_OFFICER
    )
    
    db.add_all([inst_user1, inst_user2, trainer1, trainer2, trainer3, trainer4] + students + [prog_manager, monitoring])
    db.commit()
    print(f"  ✓ Created 4 trainers, 15 students, programme manager, monitoring officer, and institution admins")
    
    print("Creating batches...")
    batch1 = Batch(name="Python Basics Batch 1", institution_id=institution1.id)
    batch2 = Batch(name="Web Development Batch 1", institution_id=institution1.id)
    batch3 = Batch(name="Data Science Batch 1", institution_id=institution2.id)
    db.add_all([batch1, batch2, batch3])
    db.commit()
    db.refresh(batch1)
    db.refresh(batch2)
    db.refresh(batch3)
    print(f"  ✓ Created 3 batches")
    
    print("Assigning trainers to batches...")
    # Assign trainers to batches
    batch_trainer1 = BatchTrainer(batch_id=batch1.id, trainer_id=trainer1.id)
    batch_trainer2 = BatchTrainer(batch_id=batch1.id, trainer_id=trainer2.id)
    batch_trainer3 = BatchTrainer(batch_id=batch2.id, trainer_id=trainer2.id)
    batch_trainer4 = BatchTrainer(batch_id=batch3.id, trainer_id=trainer3.id)
    batch_trainer5 = BatchTrainer(batch_id=batch3.id, trainer_id=trainer4.id)
    db.add_all([batch_trainer1, batch_trainer2, batch_trainer3, batch_trainer4, batch_trainer5])
    db.commit()
    print(f"  ✓ Assigned trainers to batches")
    
    print("Enrolling students in batches...")
    # Enroll students in batches
    for i, student in enumerate(students):
        if i < 8:
            db.add(BatchStudent(batch_id=batch1.id, student_id=student.id))
            if i < 5:
                db.add(BatchStudent(batch_id=batch2.id, student_id=student.id))
        else:
            db.add(BatchStudent(batch_id=batch3.id, student_id=student.id))
    db.commit()
    print(f"  ✓ Enrolled students in batches")
    
    print("Creating sessions...")
    # Create sessions
    now = datetime.utcnow()
    session_dates = [
        now - timedelta(days=7),
        now - timedelta(days=5),
        now - timedelta(days=3),
        now - timedelta(days=1),
        now + timedelta(days=1),
        now + timedelta(days=3),
        now + timedelta(days=5),
        now + timedelta(days=7),
    ]
    
    sessions = []
    for i, session_date in enumerate(session_dates):
        if i < 3:
            session = SessionModel(
                batch_id=batch1.id,
                trainer_id=trainer1.id,
                title=f"Python Basics Session {i+1}",
                date=session_date,
                start_time="10:00",
                end_time="12:00"
            )
        elif i < 5:
            session = SessionModel(
                batch_id=batch2.id,
                trainer_id=trainer2.id,
                title=f"Web Development Session {i-2}",
                date=session_date,
                start_time="14:00",
                end_time="16:00"
            )
        else:
            session = SessionModel(
                batch_id=batch3.id,
                trainer_id=trainer3.id,
                title=f"Data Science Session {i-4}",
                date=session_date,
                start_time="09:00",
                end_time="11:00"
            )
        sessions.append(session)
    
    db.add_all(sessions)
    db.commit()
    for session in sessions:
        db.refresh(session)
    print(f"  ✓ Created 8 sessions")
    
    print("Creating attendance records...")
    # Create attendance records
    attendance_records = []
    for session in sessions:
        batch = db.query(Batch).filter(Batch.id == session.batch_id).first()
        enrolled_students = db.query(BatchStudent).filter(BatchStudent.batch_id == batch.id).all()
        
        for enrolled in enrolled_students:
            # Randomly assign attendance status
            import random
            status_choice = random.choice([
                AttendanceStatus.PRESENT,
                AttendanceStatus.PRESENT,
                AttendanceStatus.PRESENT,
                AttendanceStatus.LATE,
                AttendanceStatus.ABSENT
            ])
            
            attendance = Attendance(
                session_id=session.id,
                student_id=enrolled.student_id,
                status=status_choice,
                marked_at=session.date + timedelta(hours=1)
            )
            attendance_records.append(attendance)
    
    db.add_all(attendance_records)
    db.commit()
    print(f"  ✓ Created {len(attendance_records)} attendance records")
    
    print("\n✅ Database seeding completed successfully!")
    print("\nTest Accounts:")
    print("  Student:           student1@example.com / password123")
    print("  Trainer:           trainer1@example.com / password123")
    print("  Institution:       institution1@example.com / password123")
    print("  Programme Manager: pm@example.com / password123")
    print("  Monitoring Officer: monitoring@example.com / password123")

except Exception as e:
    print(f"❌ Error during seeding: {e}")
    db.rollback()
finally:
    db.close()
