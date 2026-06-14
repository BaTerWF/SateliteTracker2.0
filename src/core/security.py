from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional

from src.models import APIKey
from src.database import SessionLocal


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """Validate API key from X-API-Key header."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing. Please provide X-API-Key header.",
        )

    db: Session = SessionLocal()
    try:
        key_obj = db.query(APIKey).filter_by(key=api_key, is_active=True).first()
        if not key_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key.",
            )
        return api_key
    finally:
        db.close()


def verify_api_key(api_key: str, db: Session) -> Optional[APIKey]:
    """Verify API key and return the key object if valid."""
    return db.query(APIKey).filter_by(key=api_key, is_active=True).first()
