# SkillBridge Quick Start Guide

## TL;DR - Get Started in 5 Minutes

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your PostgreSQL connection string

# 3. Run database seed (creates test data)
python -m src.seed

# 4. Start the API
uvicorn src.main:app --reload

# 5. Test it!
curl http://localhost:8000/health
```

## Login with Test Accounts

All passwords: `password123`

```bash
# Student
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student1@example.com", "password": "password123"}'

# Trainer  
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "trainer1@example.com", "password": "password123"}'
```

## Test the API

```bash
# Get your JWT token first
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student1@example.com", "password": "password123"}' | jq -r '.access_token')

# Mark attendance
curl -X POST http://localhost:8000/attendance/mark \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "session_id": 1,
    "status": "present"
  }'
```

## Run Tests

```bash
pytest tests/ -v
```

## API Documentation

Interactive API docs at: `http://localhost:8000/docs`

## Project Structure

```
skillbridge/
├── src/                    # Main application code
│   ├── main.py            # FastAPI app entry point
│   ├── models.py          # Database models
│   ├── routes_*.py        # API endpoints
│   ├── auth.py            # JWT & password utilities
│   └── seed.py            # Database seeding
├── tests/
│   └── test_api.py        # Pytest tests
├── README.md              # Full documentation
└── requirements.txt       # Python dependencies
```

## Common Issues

**PostgreSQL connection error?**
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Try with localhost:5432

**ModuleNotFoundError?**
- Run from project root
- Ensure virtual environment is activated

**Tests failing?**
- Delete test database if exists
- Run: `pytest tests/ -v --tb=short`

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [API docs](http://localhost:8000/docs) in browser
3. Review [models.py](src/models.py) for database schema
4. Explore [routes_*.py](src/) for endpoint implementations
