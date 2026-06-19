from pydantic import BaseModel, ConfigDict
from typing import Optional


class StationBase(BaseModel):
    """Base observer station schema."""
    name: str
    latitude: float
    longitude: float
    altitude: float = 0.0


class StationCreate(StationBase):
    """Schema for creating an observer station."""
    pass


class StationResponse(StationBase):
    """Schema for station response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class StationUpdate(StationBase):
    """Schema for updating an observer station."""
    pass
