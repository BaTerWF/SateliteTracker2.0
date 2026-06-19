from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class TLEResponse(BaseModel):
    """Schema for TLE data response."""
    id: int
    satellite_id: str
    epoch: datetime
    bstar: float
    inclination: float
    raan: float
    eccentricity: float
    arg_perigee: float
    mean_anomaly: float
    mean_motion: float
    rev_num_at_epoch: int
    line1: str
    line2: str

    model_config = ConfigDict(from_attributes=True)


class SatellitePosition(BaseModel):
    """Schema for satellite position data."""
    time: datetime
    latitude: float
    longitude: float
    altitude_km: float
    speed_kmh: float
    ecef: dict


class OrbitPathPoint(BaseModel):
    """Schema for a single point in orbit path."""
    time: str
    lat: float
    lon: float
    alt: float


class OrbitPath(BaseModel):
    """Schema for orbit path response."""
    satellite_id: str
    points: List[OrbitPathPoint]
    generated_at: datetime


class PositionQuery(BaseModel):
    """Schema for position query parameters."""
    timestamp: Optional[datetime] = None


class OrbitQuery(BaseModel):
    """Schema for orbit path query parameters."""
    points_count: int = 100
    timestamp: Optional[datetime] = None
