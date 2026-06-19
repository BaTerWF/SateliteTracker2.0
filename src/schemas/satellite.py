from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class SatelliteBase(BaseModel):
    """Base satellite schema."""
    name: str
    intl_designator: Optional[str] = None


class SatelliteCreate(SatelliteBase):
    """Schema for creating a satellite."""
    norad_id: str


class SatelliteResponse(SatelliteBase):
    """Schema for satellite response."""
    norad_id: str
    model_config = ConfigDict(from_attributes=True)


class SatelliteDetail(SatelliteResponse):
    """Schema for satellite detail with latest TLE."""
    latest_tle: Optional["TLEResponse"] = None

    model_config = ConfigDict(from_attributes=True)


# Import TLEResponse for forward reference
from src.schemas.tle import TLEResponse

SatelliteDetail.model_rebuild()


class SatelliteFromCelestrak(BaseModel):
    """Schema for fetching satellites from Celestrak."""
    group: str  # e.g., 'stations', 'starlink', 'gps', etc.
