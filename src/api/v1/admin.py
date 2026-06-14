from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
from datetime import datetime

from src.api.deps import get_db, get_current_api_key
from src.models import APIKey
from src.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse


router = APIRouter()


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return f"stk_{secrets.token_urlsafe(32)}"


@router.post("/api-keys", response_model=APIKeyCreateResponse)
def create_api_key(
    key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new API key.

    The key will be returned only once, so save it securely.
    """
    # Check if API key with same name exists
    existing = db.query(APIKey).filter(APIKey.name == key_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"API key with name '{key_data.name}' already exists"
        )

    new_key_str = generate_api_key()

    new_key = APIKey(
        key=new_key_str,
        name=key_data.name,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return APIKeyCreateResponse(
        id=new_key.id,
        key=new_key.key,
        name=new_key.name,
        is_active=new_key.is_active,
        created_at=new_key.created_at
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List all API keys (without exposing the actual key values).
    """
    keys = db.query(APIKey).all()

    # Return masked keys for security
    return [
        APIKeyResponse(
            id=key.id,
            key="****" + key.key[-4:] if len(key.key) > 4 else "****",
            name=key.name,
            is_active=key.is_active,
            created_at=key.created_at
        )
        for key in keys
    ]


@router.delete("/api-keys/{key_id}", response_model=dict)
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Delete an API key.
    """
    key = db.query(APIKey).filter(APIKey.id == key_id).first()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found"
        )

    db.delete(key)
    db.commit()

    return {
        "status": "deleted",
        "key_id": key_id,
        "name": key.name
    }
