from pydantic import BaseModel, ConfigDict
from datetime import datetime


class APIKeyBase(BaseModel):
    """Base API key schema."""
    name: str


class APIKeyCreate(APIKeyBase):
    """Schema for creating an API key."""
    pass


class APIKeyResponse(APIKeyBase):
    """Schema for API key response."""
    id: int
    key: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreateResponse(BaseModel):
    """Schema for API key creation response (shows key only once)."""
    id: int
    key: str
    name: str
    is_active: bool
    created_at: datetime
