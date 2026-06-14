from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.core.config import settings
from src.api.v1.api import api_router
from src.services.scheduler import scheduler
from src.database import engine
from src.models import Base


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up SatelliteTracker API")

    # Create database tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Start the scheduler
    try:
        scheduler.start()
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")

    yield

    # Shutdown
    logger.info("Shutting down SatelliteTracker API")
    scheduler.shutdown()
    logger.info("Background scheduler shutdown")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "A database error occurred. Please try again later.",
            "error": str(exc)
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    logger.error(f"Value error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "error": "ValueError"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed",
            "errors": exc.errors()
        }
    )


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "SatelliteTracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SatelliteTracker API"
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
