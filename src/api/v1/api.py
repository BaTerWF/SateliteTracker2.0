from fastapi import APIRouter
from src.api.v1 import satellites, stations, admin


api_router = APIRouter()

# Include satellite routes
api_router.include_router(
    satellites.router,
    prefix="/satellites",
    tags=["satellites"]
)

# Include station routes
api_router.include_router(
    stations.router,
    prefix="/stations",
    tags=["stations"]
)

# Include admin routes
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)
