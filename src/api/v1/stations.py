from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from src.api.deps import get_db, get_current_api_key
from src.models import ObserverStation
from src.schemas.station import StationCreate, StationResponse, StationUpdate


router = APIRouter()


@router.post("/", response_model=StationResponse)
def create_station(
    station: StationCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new observer station.
    """
    # Check if station with same name exists
    existing = db.query(ObserverStation).filter(ObserverStation.name == station.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Station with name '{station.name}' already exists"
        )

    new_station = ObserverStation(
        name=station.name,
        latitude=station.latitude,
        longitude=station.longitude,
        altitude=station.altitude
    )

    db.add(new_station)
    db.commit()
    db.refresh(new_station)

    return new_station


@router.get("/", response_model=List[StationResponse])
def list_stations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List all observer stations.
    """
    stations = db.query(ObserverStation).offset(skip).limit(limit).all()
    return stations


@router.get("/{station_id}", response_model=StationResponse)
def get_station(
    station_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get observer station details.
    """
    station = db.query(ObserverStation).filter(ObserverStation.id == station_id).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observer station with ID {station_id} not found"
        )

    return station


@router.delete("/{station_id}", response_model=dict)
def delete_station(
    station_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Delete an observer station.
    """
    station = db.query(ObserverStation).filter(ObserverStation.id == station_id).first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observer station with ID {station_id} not found"
        )

    db.delete(station)
    db.commit()

    return {
        "status": "deleted",
        "station_id": station_id,
        "name": station.name
    }
