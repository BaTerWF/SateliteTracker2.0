from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SatelliteTracker API"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Celestrak Configuration
    CELESTRAK_BASE_URL: str = "https://celestrak.org/NORAD/elements/gp.php"
    CELESTRAK_GROUP_URL: str = "https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle"
    CELESTRAK_SATELLITE_URL: str = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"

    # Background Task Configuration
    TLE_UPDATE_INTERVAL_HOURS: int = 24  # Update TLE data every 24 hours
    TLE_UPDATE_TIME: str = "00:00"  # Update time (UTC)

    # Database
    DATABASE_URL: str = "sqlite:///satellites.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
