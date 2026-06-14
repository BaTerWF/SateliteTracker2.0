import httpx
from typing import List, Optional
from sqlalchemy.orm import Session

from src.models import Satellite, TLE_Data
from src.services.parse_tle import parse_tle_to_dict, save_tle_to_db
from src.core.config import settings


class CelestrakService:
    """Service for interacting with Celestrak API."""

    def __init__(self):
        self.base_url = settings.CELESTRAK_BASE_URL
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def fetch_tle_group(self, group: str) -> List[str]:
        """
        Fetch TLE data for a satellite group from Celestrak.

        Args:
            group: Group name (e.g., 'stations', 'starlink', 'gps', etc.)

        Returns:
            List of TLE line strings (3 lines per satellite: name, line1, line2)
        """
        url = settings.CELESTRAK_GROUP_URL.format(group=group)

        response = await self.client.get(url)
        response.raise_for_status()

        tle_text = response.text
        tle_lines = tle_text.strip().split('\n')

        return tle_lines

    async def fetch_satellite_tle(self, norad_id: str) -> Optional[List[str]]:
        """
        Fetch TLE data for a specific satellite from Celestrak.

        Args:
            norad_id: NORAD catalog ID

        Returns:
            List of 3 strings [name, line1, line2] or None if not found
        """
        url = settings.CELESTRAK_SATELLITE_URL.format(norad_id=norad_id)

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            tle_text = response.text.strip()
            tle_lines = tle_text.split('\n')

            if len(tle_lines) >= 2:
                # Celestrak returns name, line1, line2
                return tle_lines
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def import_to_database(
        self,
        tle_lines: List[str],
        db: Session,
        group_name: Optional[str] = None
    ) -> int:
        """
        Parse and import TLE data to database.

        Args:
            tle_lines: List of TLE strings (name, line1, line2 format)
            db: Database session
            group_name: Optional group name for logging

        Returns:
            Number of satellites imported
        """
        count = 0
        i = 0

        while i < len(tle_lines):
            if i + 2 >= len(tle_lines):
                break

            name = tle_lines[i].strip()
            line1 = tle_lines[i + 1].strip()
            line2 = tle_lines[i + 2].strip()

            # Validate TLE format
            if not line1.startswith('1 ') or not line2.startswith('2 '):
                i += 1
                continue

            try:
                parsed_data = parse_tle_to_dict(line1, line2)
                save_tle_to_db(db, parsed_data, satellite_name=name)
                count += 1
            except Exception as e:
                print(f"Error parsing TLE for {name}: {e}")

            i += 3

        db.commit()
        print(f"Imported {count} satellites from group '{group_name}'")
        return count

    async def fetch_and_import_group(
        self,
        group: str,
        db: Session
    ) -> dict:
        """
        Fetch and import a satellite group from Celestrak.

        Args:
            group: Group name (e.g., 'stations', 'starlink', 'gps')
            db: Database session

        Returns:
            Dict with import results
        """
        tle_lines = await self.fetch_tle_group(group)
        count = await self.import_to_database(tle_lines, db, group)

        return {
            "group": group,
            "satellites_imported": count,
            "status": "success"
        }

    async def update_satellite(
        self,
        norad_id: str,
        db: Session
    ) -> Optional[dict]:
        """
        Update TLE data for a specific satellite.

        Args:
            norad_id: NORAD catalog ID
            db: Database session

        Returns:
            Dict with update results or None if satellite not found
        """
        tle_lines = await self.fetch_satellite_tle(norad_id)

        if not tle_lines:
            return None

        name = tle_lines[0].strip()
        line1 = tle_lines[1].strip()
        line2 = tle_lines[2].strip()

        parsed_data = parse_tle_to_dict(line1, line2)
        save_tle_to_db(db, parsed_data, satellite_name=name)
        db.commit()

        return {
            "norad_id": norad_id,
            "name": name,
            "status": "updated"
        }


async def fetch_and_import_group(group: str, db: Session) -> dict:
    """Convenience function to fetch and import a satellite group."""
    async with CelestrakService() as service:
        return await service.fetch_and_import_group(group, db)


async def update_satellite_tle(norad_id: str, db: Session) -> Optional[dict]:
    """Convenience function to update a specific satellite's TLE."""
    async with CelestrakService() as service:
        return await service.update_satellite(norad_id, db)
