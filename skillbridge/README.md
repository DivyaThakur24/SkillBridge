# SkillBridge - Attendance Management System API

A role-based attendance management system for a state-level skilling programme with JWT authentication and comprehensive access control.

## Overview

SkillBridge is a FastAPI-based REST API for managing attendance across multiple institutions, batches, sessions, and user roles. The system supports five distinct roles with granular permission levels and includes dual-token authentication for the Monitoring Officer role.

### Key Features
- ✅ Role-based access control (RBAC) on all protected endpoints
- ✅ JWT-based authentication with 24-hour token expiry
- ✅ Dual-token system for Monitoring Officer (login + scoped monitoring token)
- ✅ Comprehensive attendance tracking
- ✅ Batch invite system with token expiry
- ✅ Attendance summaries at batch, institution, and programme levels
- ✅ Full validation and error handling with proper HTTP status codes
- ✅ Pytest test suite with real database integration

## Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI 0.104.1 |
| Database | PostgreSQL (SQLAlchemy ORM) |
| Authentication | PyJWT + Passlib/Bcrypt |
| Testing | Pytest + HTTPx |
| Deployment | Railway/Render/Fly.io (ready) |

## Local Setup

### Prerequisites
- Python 3.8+
- pip
- PostgreSQL (or any supported database via SQLAlchemy)

### Installation

1. **Clone/Create project:**
   ```bash
   cd skillbridge
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   Update `DATABASE_URL` with your PostgreSQL connection string.

5. **Seed database:**
   ```bash
   python -m src.seed
   ```
   This creates 2 institutions, 4 trainers, 15 students, 3 batches, and 8 sessions with attendance records.

6. **Run server:**
   ```bash
   uvicorn src.main:app --reload
   ```
   API available at `http://localhost:8000`

## API Documentation

Auto-generated docs available at `/docs` (Swagger UI)

### Authentication Endpoints

#### POST `/auth/signup`
Sign up a new user and receive JWT.

**Request:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Student",
    "email": "john@example.com",
    "password": "securepass123",
    "role": "student",
    "institution_id": null
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/auth/login`
Log in and receive JWT.

**Request:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "trainer1@example.com", "password": "password123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/auth/monitoring-token`
Get a scoped monitoring token (Monitoring Officer only).

**Request:**
```bash
# First, get monitoring officer JWT via login
MONITORING_JWT=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "email=monitoring@example.com&password=password123" | jq -r '.access_token')

# Then exchange for monitoring token
curl -X POST http://localhost:8000/auth/monitoring-token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONITORING_JWT" \
  -d '{"key": "monitoring-api-key-123"}'
```

**Response:**
```json
{
  "monitoring_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Batch Endpoints

#### POST `/batches`
Create a batch (Trainer/Institution only).

**Request:**
```bash
curl -X POST http://localhost:8000/batches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAINER_JWT" \
  -d '{
    "name": "Python Advanced",
    "institution_id": 1
  }'
```

#### POST `/batches/{batch_id}/invite`
Generate invite token (Trainer only).

**Request:**
```bash
curl -X POST http://localhost:8000/batches/1/invite \
  -H "Authorization: Bearer $TRAINER_JWT"
```

**Response:**
```json
{
  "token": "6K5_x8y9P2Qz...",
  "expires_at": "2026-05-02T10:30:00"
}
```

#### POST `/batches/join`
Join batch using invite token (Student only).

**Request:**
```bash
curl -X POST http://localhost:8000/batches/join \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_JWT" \
  -d '{"token": "6K5_x8y9P2Qz..."}'
```

### Session Endpoints

#### POST `/sessions`
Create session (Trainer only).

**Request:**
```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAINER_JWT" \
  -d '{
    "batch_id": 1,
    "title": "Python Basics - Loops",
    "date": "2026-04-25T10:00:00",
    "start_time": "10:00",
    "end_time": "12:00"
  }'
```

#### GET `/sessions/{session_id}/attendance`
Get session attendance (Trainer only).

**Request:**
```bash
curl -X GET http://localhost:8000/sessions/1/attendance \
  -H "Authorization: Bearer $TRAINER_JWT"
```

### Attendance Endpoints

#### POST `/attendance/mark`
Mark attendance (Student only).

**Request:**
```bash
curl -X POST http://localhost:8000/attendance/mark \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_JWT" \
  -d '{
    "session_id": 1,
    "status": "present"
  }'
```

### Summary Endpoints

#### GET `/institutions/{institution_id}/summary`
Institution summary (Programme Manager only).

**Request:**
```bash
curl -X GET http://localhost:8000/institutions/1/summary \
  -H "Authorization: Bearer $PM_JWT"
```

**Response:**
```json
{
  "institution_id": 1,
  "institution_name": "Tech Institute",
  "total_batches": 3,
  "total_students": 12,
  "attendance_rate": 85.5
}
```

#### GET `/programme/summary`
Programme-wide summary (Programme Manager only).

**Request:**
```bash
curl -X GET http://localhost:8000/programme/summary \
  -H "Authorization: Bearer $PM_JWT"
```

#### GET `/monitoring/attendance`
Full attendance data (Monitoring Officer only - requires scoped token).

**Request:**
```bash
curl -X GET http://localhost:8000/monitoring/attendance \
  -H "Authorization: Bearer $MONITORING_TOKEN"
```

## Test Accounts

All test accounts have password: `password123`

| Role | Email | Password |
|------|-------|----------|
| **Student** | student1@example.com | password123 |
| **Trainer** | trainer1@example.com | password123 |
| **Institution** | institution1@example.com | password123 |
| **Programme Manager** | pm@example.com | password123 |
| **Monitoring Officer** | monitoring@example.com | password123 |

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py::test_student_signup_and_login -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

The test suite includes:
1. ✅ Student signup and login with JWT validation
2. ✅ Trainer creating sessions with required fields
3. ✅ Student marking attendance
4. ✅ POST to `/monitoring/attendance` returns 405
5. ✅ Protected endpoints return 401 without token

At least 2 tests hit a real (test) database using SQLAlchemy fixtures.

## Database Schema

### Core Entities

**Users**
- `id` (INT, PK)
- `name` (VARCHAR)
- `email` (VARCHAR, unique)
- `hashed_password` (VARCHAR)
- `role` (ENUM: student/trainer/institution/programme_manager/monitoring_officer)
- `institution_id` (INT, FK, nullable)
- `created_at` (TIMESTAMP)

**Institutions**
- `id` (INT, PK)
- `name` (VARCHAR)
- `created_at` (TIMESTAMP)

**Batches**
- `id` (INT, PK)
- `name` (VARCHAR)
- `institution_id` (INT, FK)
- `created_at` (TIMESTAMP)

**Batch Trainers** (Many-to-Many)
- `batch_id` (INT, FK, PK)
- `trainer_id` (INT, FK, PK)

**Batch Students** (Many-to-Many)
- `batch_id` (INT, FK, PK)
- `student_id` (INT, FK, PK)

**Batch Invites**
- `id` (INT, PK)
- `batch_id` (INT, FK)
- `token` (VARCHAR, unique)
- `created_by` (INT, FK)
- `expires_at` (TIMESTAMP)
- `used` (BOOLEAN)

**Sessions**
- `id` (INT, PK)
- `batch_id` (INT, FK)
- `trainer_id` (INT, FK)
- `title` (VARCHAR)
- `date` (DATETIME)
- `start_time` (VARCHAR, HH:MM)
- `end_time` (VARCHAR, HH:MM)
- `created_at` (TIMESTAMP)

**Attendance**
- `id` (INT, PK)
- `session_id` (INT, FK)
- `student_id` (INT, FK)
- `status` (ENUM: present/absent/late)
- `marked_at` (TIMESTAMP)

## JWT Payload Structure

### Standard Login Token
```json
{
  "user_id": 1,
  "role": "student",
  "email": "student@example.com",
  "iat": 1682000000,
  "exp": 1682086400
}
```

### Monitoring Officer Scoped Token
```json
{
  "user_id": 5,
  "role": "monitoring_officer",
  "scope": "monitoring",
  "iat": 1682000000,
  "exp": 1682003600
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input (e.g., expired invite)
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `405 Method Not Allowed` - Wrong HTTP method
- `422 Unprocessable Entity` - Validation error

### Example Error Response
```json
{
  "detail": "Only students can mark attendance"
}
```

## Deployment

### Prerequisites
- PostgreSQL database (e.g., Neon)
- Deployment platform (Railway, Render, or Fly.io)
- Environment variables configured

### Deployment Steps

#### Railway
1. Push code to GitHub
2. Connect repository to Railway
3. Configure environment variables
4. Deploy

#### Render
1. Create Web Service
2. Connect GitHub repository
3. Set environment variables
4. Deploy

#### Fly.io
```bash
fly launch
fly secrets set DATABASE_URL="..."
fly deploy
```

### Live Deployment

**Base URL:** (Update after deployment)

**Example curl to live deployment:**
```bash
curl -X POST https://skillbridge-api.railway.app/auth/login \
  -d "email=student1@example.com&password=password123"
```

## Security Considerations

### Current Implementation
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with 24-hour expiry
- ✅ Role-based access control on all protected endpoints
- ✅ Monitoring Officer has scoped tokens (1-hour expiry)
- ✅ API key validation for monitoring token generation

### Known Security Issues & Solutions

**Issue 1: Hardcoded API Key**
- **Current:** API key hardcoded in `.env`
- **Fix:** Use external secrets manager (AWS Secrets Manager, HashiCorp Vault)

**Issue 2: No Token Revocation**
- **Current:** Tokens valid until expiry
- **Fix:** Implement token blacklist (Redis) or JWT with jti (JWT ID) claim

**Issue 3: No HTTPS Enforcement**
- **Current:** API accepts HTTP
- **Fix:** Deploy behind HTTPS reverse proxy, use HSTS headers

**Issue 4: Database Credentials in Connection String**
- **Current:** Credentials in DATABASE_URL
- **Fix:** Use managed database services with IAM authentication

**Issue 5: No Rate Limiting**
- **Current:** No protection against brute force
- **Fix:** Add rate limiting middleware (slowapi)

## Schema Decisions

### Batch Trainers (Many-to-Many)
Multiple trainers can be assigned to the same batch. This allows:
- Co-teaching scenarios
- Trainer coverage during absences
- Institutional flexibility

```
One Batch → Many Trainers
One Trainer → Many Batches
```

### Batch Invites
Separate invite entities with token-based joining instead of direct enrollment:
- **Why:** Self-service onboarding without admin intervention
- **Token:** URL-safe 32-char token, 7-day expiry
- **Used flag:** Prevents multiple uses of same token
- **Scalability:** Supports asynchronous enrollment workflows

### Dual-Token Monitoring Officer
Standard JWT + scoped monitoring token for Monitoring Officer:
- **Why:** Extra layer of security for read-only access across entire programme
- **Benefit:** Rotating monitoring tokens doesn't require re-login
- **Scope field:** Ensures token is scoped to monitoring endpoints only

## What's Fully Working

- ✅ All 8 core endpoints (auth, batches, sessions, attendance)
- ✅ 7 summary/read endpoints with proper RBAC
- ✅ JWT authentication with correct payload structure
- ✅ Dual-token system for Monitoring Officer
- ✅ Role-based access control on all protected routes
- ✅ Database schema with proper relationships
- ✅ Test data seeding script
- ✅ Comprehensive error handling
- ✅ 5 passing pytest tests with real database

## What's Partially Done

- ⚠️ Deployment: Code is deployment-ready but not yet live
- ⚠️ API documentation: Swagger docs auto-generated at `/docs`

## What Was Skipped

- ❌ Rate limiting middleware (use slowapi library)
- ❌ Token blacklist/revocation system (add Redis)
- ❌ Email notifications for invite links
- ❌ Batch edit/delete endpoints
- ❌ User profile update endpoints
- ❌ Database migrations (use Alembic)

## Things I'd Do Differently with More Time

1. **Token Management**
   - Implement JWT refresh tokens (2 types: access + refresh)
   - Add token blacklist with Redis for revocation
   - Implement token rotation on each refresh

2. **Monitoring & Observability**
   - Add structured logging (using Python's logging module with JSON)
   - Add request/response middleware for monitoring
   - Add Prometheus metrics for attendance accuracy

3. **Database**
   - Use Alembic for schema migrations
   - Add database connection pooling configuration
   - Add indexes on frequently queried columns

4. **Testing**
   - Add integration tests for full user flows
   - Add load testing with Locust
   - Add database transaction rollback for test isolation

5. **API Improvements**
   - Implement pagination for summary endpoints
   - Add filtering/sorting on batch and session listings
   - Add batch edit/delete endpoints with soft deletes
   - Add user profile endpoints

6. **Security**
   - Implement CORS with specific origins
   - Add CSRF protection for state-changing operations
   - Use environment-specific JWT algorithms
   - Add API key rotation mechanism

## Implementation Notes

- **Framework Choice:** FastAPI for type safety, automatic validation, and OpenAPI docs
- **Authentication:** PyJWT over python-jose for simplicity; passlib+bcrypt for password security
- **Database:** SQLAlchemy ORM for flexibility and migration to other databases
- **Validation:** Pydantic models for request/response validation

## File Structure

```
skillbridge/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Settings/environment
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic request/response models
│   ├── auth.py                 # JWT & password utilities
│   ├── routes_auth.py          # Auth endpoints
│   ├── routes_batches.py       # Batch endpoints
│   ├── routes_sessions.py      # Session & attendance endpoints
│   ├── routes_summaries.py     # Summary & monitoring endpoints
│   └── seed.py                 # Database seeding script
├── tests/
│   └── test_api.py             # Pytest tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
└── CONTACT.txt                 # Contact information
```

## Troubleshooting

**Issue: `ModuleNotFoundError: No module named 'src'`**
- Solution: Run from project root, ensure `.env` is configured

**Issue: `psycopg2.OperationalError: could not connect to server`**
- Solution: Check DATABASE_URL in `.env`, ensure PostgreSQL is running

**Issue: `Tests fail with "User not found"`**
- Solution: Clear database before running tests; fixtures handle this

## Support

For questions or issues, refer to:
- Swagger docs: `http://localhost:8000/docs`
- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy ORM tutorial: https://docs.sqlalchemy.org
