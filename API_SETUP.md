# SatelliteTracker API - Setup Guide

## Overview
SatelliteTracker API is a FastAPI-based RESTful API for tracking satellites, calculating their positions, and managing observer stations.

## Installation

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run Setup Script
This creates database tables and an initial API key:
```bash
python setup_api.py
```

### 3. Start the Server
```bash
uvicorn main:app --reload
```

Or simply:
```bash
python main.py
```

The API will be available at: http://localhost:8000

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Authentication

All endpoints (except root and health check) require an API key via the `X-API-Key` header.

### Example Request
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/satellites/
```

## Quick Start Guide

### 1. Fetch Satellites from Celestrak
Import satellite groups (stations, starlink, gps, etc.):

```bash
curl -X POST "http://localhost:8000/api/v1/satellites/from-celestrak" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"group": "stations"}'
```

Available groups: `stations`, `starlink`, `gps`, `iridium`, `active`, etc.

### 2. List Satellites
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/satellites/
```

### 3. Get Satellite Position
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/satellites/25544/position
```

### 4. Get Orbit Path
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/v1/satellites/25544/orbit?points_count=100
```

### 5. Create Observer Station
```bash
curl -X POST "http://localhost:8000/api/v1/stations/" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Station",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 10.0
  }'
```

## API Endpoints

### Satellites
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/satellites/from-celestrak` | Fetch satellite group |
| GET | `/api/v1/satellites/` | List all satellites |
| GET | `/api/v1/satellites/{norad_id}` | Get satellite details |
| PUT | `/api/v1/satellites/{norad_id}` | Update TLE from Celestrak |
| GET | `/api/v1/satellites/{norad_id}/position` | Get current position |
| GET | `/api/v1/satellites/{norad_id}/orbit` | Get orbit path |
| GET | `/api/v1/satellites/{norad_id}/tle/history` | Get TLE history |
| DELETE | `/api/v1/satellites/{norad_id}` | Delete satellite |

### Stations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/stations/` | Create observer station |
| GET | `/api/v1/stations/` | List stations |
| GET | `/api/v1/stations/{station_id}` | Get station details |
| DELETE | `/api/v1/stations/{station_id}` | Delete station |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/admin/api-keys` | Create new API key |
| GET | `/api/v1/admin/api-keys` | List all API keys |
| DELETE | `/api/v1/admin/api-keys/{key_id}` | Delete API key |

## Background Tasks

The API includes a scheduler for automatic TLE updates:

- **Default Schedule**: Daily at 00:00 UTC
- **Configured in**: `src/core/config.py`
- **Implementation**: `src/services/scheduler.py`

To modify the schedule, edit `src/core/config.py`:

```python
TLE_UPDATE_INTERVAL_HOURS: int = 24  # Update interval
TLE_UPDATE_TIME: str = "00:00"      # Update time (UTC)
```

## Common Issues

### Database Migration Issues
If you encounter database migration issues:

```bash
# Drop and recreate database
rm satellites.db
python setup_api.py
```

### Port Already in Use
If port 8000 is in use:

```bash
uvicorn main:app --port 8080 --reload
```

### CORS Issues
To allow additional origins, edit `src/core/config.py`:

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://your-frontend-url.com",
]
```

## Configuration

Environment variables (optional):

```bash
# Create .env file
echo "TLE_UPDATE_TIME=02:00" > .env
echo "DATABASE_URL=sqlite:///custom.db" >> .env
```

## Development

### Project Structure
```
src/
├── api/              # API routes
│   ├── deps.py       # Dependencies (DB, auth)
│   └── v1/           # API v1 endpoints
│       ├── api.py    # Route aggregation
│       ├── satellites.py
│       ├── stations.py
│       └── admin.py
├── core/             # Core functionality
│   ├── config.py     # Settings
│   └── security.py   # API key auth
├── schemas/          # Pydantic schemas
├── services/         # Business logic
│   ├── celestrak.py  # Celestrak integration
│   ├── calculator.py # Orbit calculations
│   ├── parse_tle.py  # TLE parsing
│   └── scheduler.py  # Background tasks
├── models.py         # SQLAlchemy models
└── database.py       # Database configuration
```

### Testing
```bash
# Start server
uvicorn main:app --reload

# In another terminal, test endpoints
curl http://localhost:8000/health
curl -H "X-API-Key: your-key" http://localhost:8000/api/v1/satellites/
```

## Production Deployment

For production deployment:

1. **Use a production WSGI server**:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set environment variables**:
   ```bash
   export DATABASE_URL=postgresql://user:pass@host/db
   export CORS_ORIGINS=["https://your-domain.com"]
   ```

3. **Use a production database** (PostgreSQL recommended)

4. **Set up SSL/TLS** (use reverse proxy like nginx)

5. **Configure proper logging and monitoring**

## License

Your project license here.
