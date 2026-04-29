"""
Database connection and session management module.

Sets up SQLAlchemy engine for the configured database and provides
a SessionLocal factory for creating database sessions. The get_db
dependency is used throughout the API routes for dependency injection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

# Create SQLAlchemy engine with connection pool
# echo=False means SQL queries won't be printed to console (set to True for debugging)
# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(
    settings.DATABASE_URL, 
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create a factory for generating new database sessions
# autocommit=False: transactions must be explicitly committed
# autoflush=False: objects won't be flushed to database before query execution
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy ORM models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI route handlers.
    
    Yields a database session that FastAPI will inject into route handlers.
    Ensures the session is properly closed after the request completes,
    even if an exception occurs (thanks to try/finally).
    
    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
            users = db.query(User).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Always close the session to return connection to the pool
        db.close()
