from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from contextlib import contextmanager
from typing import Optional

from src.database import SessionLocal
from src.services.celestrak import CelestrakService
from src.core.config import settings


class TLEScheduler:
    """Scheduler for periodic TLE updates."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False

    def start(self):
        """Start the scheduler."""
        if not self.running:
            self.scheduler.start()
            self.running = True
            print("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            print("Scheduler shutdown")

    @contextmanager
    def get_db(self):
        """Get database session context manager."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def update_satellite_group(self, group: str):
        """
        Update TLE data for a specific satellite group.

        Args:
            group: Group name (e.g., 'stations', 'starlink')
        """
        print(f"Updating satellite group: {group}")

        db: Session = SessionLocal()
        try:
            async with CelestrakService() as service:
                result = await service.fetch_and_import_group(group, db)
                print(f"Group '{group}' updated: {result['satellites_imported']} satellites")
        except Exception as e:
            print(f"Error updating group '{group}': {e}")
            db.rollback()
        finally:
            db.close()

    async def update_all_satellites(self):
        """
        Update all tracked satellites in the database.

        This task queries all satellites and updates their TLE data from Celestrak.
        """
        print("Starting daily TLE update for all satellites")

        db: Session = SessionLocal()
        try:
            from src.models import Satellite

            satellites = db.query(Satellite).all()
            total = len(satellites)
            updated = 0
            failed = 0

            async with CelestrakService() as service:
                for satellite in satellites:
                    try:
                        result = await service.update_satellite(
                            satellite.norad_id,
                            db
                        )
                        if result:
                            updated += 1
                    except Exception as e:
                        print(f"Failed to update {satellite.norad_id}: {e}")
                        failed += 1

            print(f"Daily update complete: {updated}/{total} updated, {failed} failed")
        except Exception as e:
            print(f"Error in daily update: {e}")
        finally:
            db.close()

    def add_daily_update_job(self, group: Optional[str] = None):
        """
        Add a scheduled job for daily TLE updates.

        Args:
            group: Optional specific group to update. If None, updates all satellites.
        """
        # Schedule for daily at specified time (default 00:00 UTC)
        hour, minute = map(int, settings.TLE_UPDATE_TIME.split(':'))

        if group:
            self.scheduler.add_job(
                self.update_satellite_group,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=[group],
                id=f"daily_update_{group}",
                replace_existing=True
            )
            print(f"Scheduled daily update for group '{group}' at {hour:02d}:{minute:02d} UTC")
        else:
            self.scheduler.add_job(
                self.update_all_satellites,
                trigger=CronTrigger(hour=hour, minute=minute),
                id="daily_update_all",
                replace_existing=True
            )
            print(f"Scheduled daily update for all satellites at {hour:02d}:{minute:02d} UTC")

    def add_hourly_update_job(self, group: str):
        """
        Add an hourly update job for a specific group.

        Args:
            group: Group name to update hourly
        """
        self.scheduler.add_job(
            self.update_satellite_group,
            trigger='cron',
            hour='*',
            minute=0,
            args=[group],
            id=f"hourly_update_{group}",
            replace_existing=True
        )
        print(f"Scheduled hourly update for group '{group}'")


# Global scheduler instance
scheduler = TLEScheduler()
