from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator

from src.database import SessionLocal
from src.core.security import get_api_key


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_api_key(api_key: str = Depends(get_api_key)) -> str:
    """
    Dependency that validates and returns the current API key.

    Args:
        api_key: Validated API key from security dependency

    Returns:
        The API key string
    """
    return api_key
