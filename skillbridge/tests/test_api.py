"""
Pytest tests for SkillBridge API
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import SessionLocal, Base, engine
from src.models import User, Institution, Batch, BatchTrainer, BatchStudent, Session as SessionModel, RoleEnum
from src.auth import hash_password
from datetime import datetime, timedelta
import json

# Override database dependency to use test database
@pytest.fixture(scope="function")
def test_db():
    # Create test tables
    Base.metadata.create_all(bind=engine)
    yield SessionLocal()
    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture
def create_test_data():
    """Create test data in database"""
    db = SessionLocal()
    
    # Create institution
    institution = Institution(name="Test Institution")
    db.add(institution)
    db.commit()
    db.refresh(institution)
    
    # Create users
    student = User(
        name="Test Student",
        email="teststudent@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.STUDENT,
        institution_id=institution.id
    )
    
    trainer = User(
        name="Test Trainer",
        email="testtrainer@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.TRAINER,
        institution_id=institution.id
    )
    
    monitoring_officer = User(
        name="Monitoring Officer",
        email="monitoring@example.com",
        hashed_password=hash_password("password123"),
        role=RoleEnum.MONITORING_OFFICER
    )
    
    db.add_all([student, trainer, monitoring_officer])
    db.commit()
    db.refresh(student)
    db.refresh(trainer)
    db.refresh(monitoring_officer)
    
    # Create batch
    batch = Batch(name="Test Batch", institution_id=institution.id)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    # Assign trainer to batch
    batch_trainer = BatchTrainer(batch_id=batch.id, trainer_id=trainer.id)
    db.add(batch_trainer)
    db.commit()
    
    # Enroll student
    batch_student = BatchStudent(batch_id=batch.id, student_id=student.id)
    db.add(batch_student)
    db.commit()
    
    # Create session
    session = SessionModel(
        batch_id=batch.id,
        trainer_id=trainer.id,
        title="Test Session",
        date=datetime.utcnow(),
        start_time="10:00",
        end_time="12:00"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "student": student,
        "trainer": trainer,
        "monitoring_officer": monitoring_officer,
        "institution": institution,
        "batch": batch,
        "session": session,
        "db": db
    }


def test_student_signup_and_login(client, create_test_data):
    """Test successful student signup and login, asserting a valid JWT is returned"""
    # Signup
    signup_response = client.post(
        "/auth/signup",
        json={
            "name": "New Student",
            "email": "newstudent@example.com",
            "password": "password123",
            "role": "student"
        }
    )
    
    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert "access_token" in signup_data
    assert signup_data["token_type"] == "bearer"
    
    token = signup_data["access_token"]
    assert len(token) > 0
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "newstudent@example.com",
            "password": "password123"
        }
    )
    
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert len(login_data["access_token"]) > 0


def test_trainer_create_session(client, create_test_data):
    """Test a trainer creating a session with all required fields"""
    data = create_test_data
    
    # First, get a trainer token
    login_response = client.post(
        "/auth/login",
        json={
            "email": "testtrainer@example.com",
            "password": "password123"
        }
    )
    trainer_token = login_response.json()["access_token"]
    
    # Create session
    session_response = client.post(
        "/sessions",
        json={
            "batch_id": data["batch"].id,
            "title": "Advanced Python",
            "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "start_time": "14:00",
            "end_time": "16:00"
        },
        headers={"Authorization": f"Bearer {trainer_token}"}
    )
    
    assert session_response.status_code == 200
    session_data = session_response.json()
    assert session_data["title"] == "Advanced Python"
    assert session_data["batch_id"] == data["batch"].id
    assert session_data["trainer_id"] == data["trainer"].id
    assert session_data["start_time"] == "14:00"
    assert session_data["end_time"] == "16:00"


def test_student_mark_attendance(client, create_test_data):
    """Test a student successfully marking their own attendance"""
    data = create_test_data
    
    # Get student token
    student_response = client.post(
        "/auth/login",
        json={
            "email": "teststudent@example.com",
            "password": "password123"
        }
    )
    student_token = student_response.json()["access_token"]
    
    # Mark attendance
    attendance_response = client.post(
        "/attendance/mark",
        json={
            "session_id": data["session"].id,
            "status": "present"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert attendance_response.status_code == 200
    attendance_data = attendance_response.json()
    assert attendance_data["session_id"] == data["session"].id
    assert attendance_data["student_id"] == data["student"].id
    assert attendance_data["status"] == "present"


def test_monitoring_attendance_post_returns_405(client, create_test_data):
    """Test that a POST to /monitoring/attendance returns 405 Method Not Allowed"""
    response = client.post("/monitoring/attendance")
    
    assert response.status_code == 405


def test_protected_endpoint_without_token(client):
    """Test that a request to a protected endpoint with no token returns 401"""
    response = client.post(
        "/sessions",
        json={
            "batch_id": 1,
            "title": "Test",
            "date": datetime.utcnow().isoformat(),
            "start_time": "10:00",
            "end_time": "12:00"
        }
    )
    
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
