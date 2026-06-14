from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.api.deps import get_db, get_current_api_key
from src.models import Satellite, TLE_Data
from src.schemas.satellite import (
    SatelliteCreate,
    SatelliteResponse,
    SatelliteDetail,
    SatelliteFromCelestrak,
)
from src.schemas.tle import (
    TLEResponse,
    SatellitePosition,
    OrbitPath,
    OrbitPathPoint,
)
from src.services.celestrak import CelestrakService
from src.services.calculator import get_satellite_data, generate_orbit_path


router = APIRouter()


@router.post("/from-celestrak", response_model=dict)
async def fetch_satellites_from_celestrak(
    group_data: SatelliteFromCelestrak,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Fetch satellite group from Celestrak and import to database.

    Groups: stations, starlink, gps, iridium, etc.
    """
    async with CelestrakService() as service:
        result = await service.fetch_and_import_group(group_data.group, db)
        return result


@router.get("/", response_model=List[SatelliteResponse])
def list_satellites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List all satellites in the database.
    """
    satellites = db.query(Satellite).offset(skip).limit(limit).all()
    return satellites


@router.get("/{norad_id}", response_model=SatelliteDetail)
def get_satellite(
    norad_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get satellite details with latest TLE data.
    """
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()

    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with NORAD ID {norad_id} not found"
        )

    # Get latest TLE
    latest_tle = (
        db.query(TLE_Data)
        .filter(TLE_Data.satellite_id == norad_id)
        .order_by(TLE_Data.epoch.desc())
        .first()
    )

    response_data = SatelliteDetail.model_validate(satellite)
    if latest_tle:
        response_data.latest_tle = TLEResponse.model_validate(latest_tle)

    return response_data


@router.put("/{norad_id}", response_model=dict)
async def update_satellite_tle(
    norad_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update satellite TLE data from Celestrak.
    """
    # Check if satellite exists
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with NORAD ID {norad_id} not found"
        )

    async with CelestrakService() as service:
        result = await service.update_satellite(norad_id, db)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Satellite {norad_id} not found on Celestrak"
            )

        return result


@router.get("/{norad_id}/position", response_model=SatellitePosition)
def get_satellite_position(
    norad_id: str,
    timestamp: Optional[datetime] = Query(None, description="Calculation time (UTC). Defaults to now."),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get current or historical position of a satellite.

    Returns latitude, longitude, altitude, and speed.
    """
    # Get satellite with latest TLE
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with NORAD ID {norad_id} not found"
        )

    latest_tle = (
        db.query(TLE_Data)
        .filter(TLE_Data.satellite_id == norad_id)
        .order_by(TLE_Data.epoch.desc())
        .first()
    )

    if not latest_tle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No TLE data found for satellite {norad_id}"
        )

    # Use provided timestamp or current time
    calc_time = timestamp if timestamp else datetime.utcnow()

    try:
        position_data = get_satellite_data(latest_tle.line1, latest_tle.line2, calc_time)
        return SatellitePosition(**position_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating position: {str(e)}"
        )


@router.get("/{norad_id}/orbit", response_model=OrbitPath)
def get_satellite_orbit(
    norad_id: str,
    points_count: int = Query(100, ge=10, le=1000, description="Number of points in orbit path"),
    timestamp: Optional[datetime] = Query(None, description="Start time for orbit calculation. Defaults to now."),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Generate orbit path for one full revolution.

    Returns a list of geographic points along the satellite's orbit.
    """
    # Get satellite with latest TLE
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with NORAD ID {norad_id} not found"
        )

    latest_tle = (
        db.query(TLE_Data)
        .filter(TLE_Data.satellite_id == norad_id)
        .order_by(TLE_Data.epoch.desc())
        .first()
    )

    if not latest_tle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No TLE data found for satellite {norad_id}"
        )

    # Use provided timestamp or current time
    start_time = timestamp if timestamp else datetime.utcnow()

    try:
        orbit_points = generate_orbit_path(
            latest_tle.line1,
            latest_tle.line2,
            start_time,
            points_count=points_count
        )

        return OrbitPath(
            satellite_id=norad_id,
            points=[OrbitPathPoint(**pt) for pt in orbit_points],
            generated_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating orbit path: {str(e)}"
        )


@router.get("/{norad_id}/tle/history", response_model=List[TLEResponse])
def get_tle_history(
    norad_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get TLE history for a satellite.

    Returns historical TLE data ordered by epoch (newest first).
    """
    # Check if satellite exists
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with NORAD ID {norad_id} not found"
        )

    tle_history = (
        db.query(TLE_Data)
        .filter(TLE_Data.satellite_id == norad_id)
        .order_by(TLE_Data.epoch.desc())
        .limit(limit)
        .all()
    )

    return tle_history


@router.delete("/{norad_id}", response_model=dict)
def delete_satellite(
    norad_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Delete a satellite and all its TLE history.
    """
    satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
    if not satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Satellite with NORAD ID {norad_id} not found"
        )

    db.delete(satellite)
    db.commit()

    return {
        "status": "deleted",
        "norad_id": norad_id,
        "name": satellite.name
    }
