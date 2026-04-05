"""API dependencies."""
from typing import Generator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings


# Re-export get_db for use in endpoints
__all__ = ["get_db"]


async def get_settings():
    """Get settings instance."""
    return settings


# Placeholder for authentication (will be implemented later)
async def get_current_user():
    """Get current authenticated user."""
    # TODO: Implement authentication
    return None