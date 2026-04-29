"""
Pytest configuration file for SkillBridge API tests
"""

import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env.test", override=True)

# Set test database URL if not already set
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
