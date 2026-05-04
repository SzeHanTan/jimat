"""
Configuration module for the FastAPI application.

This file loads settings from environment variables using pydantic-settings.
"""

import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# Load .env file explicitly - handles Windows multiprocessing correctly
# Try multiple paths to handle different execution contexts
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # When run from app/
    Path.cwd() / ".env",  # Current working directory
    Path("/".join(sys.argv[0].split("\\")[:-1])) / ".env" if sys.platform == "win32" else None,
]

for env_path in env_paths:
    if env_path and env_path.exists():
        load_dotenv(env_path)
        break


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Why we use this pattern:
    - Centralized configuration (one place to change settings)
    - Environment-specific values (.env file for development, env vars for production)
    - Type-safe (Pydantic validates all settings at startup)
    """
    
    DATABASE_URL: str
    APP_NAME: str = "Expense Tracker API"
    DEBUG: bool = False
    
    class Config:
        # Tells Pydantic to read from .env file
        env_file = ".env"
        extra = "allow"  # Allow extra fields


# Global settings object - import this in other modules
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Make sure .env file exists with DATABASE_URL defined")
    raise
