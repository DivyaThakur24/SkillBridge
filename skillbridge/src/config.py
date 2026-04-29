"""
Configuration management module for SkillBridge API.

Loads environment variables from .env file using Pydantic settings.
All sensitive configuration like database URLs and API keys should be
stored in environment variables, not hardcoded in the application.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        DATABASE_URL: PostgreSQL connection string
        JWT_SECRET_KEY: Secret key for signing JWT tokens
        JWT_ALGORITHM: Algorithm used for JWT encoding (HS256 is HMAC-based)
        JWT_EXPIRATION_HOURS: Hours until JWT token expires (24 hours for standard roles)
        MONITORING_OFFICER_API_KEY: API key for Monitoring Officer dual-token auth
        MONITORING_TOKEN_EXPIRATION_MINUTES: Minutes until monitoring-scoped token expires (1 hour)
    """
    
    DATABASE_URL: str = "sqlite:///./skillbridge.db"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    MONITORING_OFFICER_API_KEY: str = "monitoring-api-key-123"
    MONITORING_TOKEN_EXPIRATION_MINUTES: int = 60
    
    class Config:
        env_file = ".env"


# Global settings instance - imported throughout the application
settings = Settings()
