"""
Task scheduler for periodic fare monitoring.

This module handles:
- Scheduling scraping tasks
- Managing job execution
- Handling task failures
- Logging execution history
"""

from typing import Callable, Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from datetime import datetime


class TaskScheduler:
    """Manage scheduled tasks for fare monitoring."""

    def __init__(self):
        """Initialize the task scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    def start(self) -> None:
        """Start the scheduler."""
        try:
            self.scheduler.start()
            logger.info("Task scheduler started")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self) -> None:
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")

    def add_hourly_job(
        self,
        job_id: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        start_delay_minutes: int = 0,
    ) -> str:
        """
        Add a job that runs every hour.

        Args:
            job_id: Unique job identifier
            func: Async function to execute
            args: Function positional arguments
            kwargs: Function keyword arguments
            start_delay_minutes: Minutes to wait before first run

        Returns:
            Job ID
        """
        if kwargs is None:
            kwargs = {}

        try:
            job = self.scheduler.add_job(
                func,
                IntervalTrigger(hours=1, minutes=start_delay_minutes),
                args=args,
                kwargs=kwargs,
                id=job_id,
                name=f"Hourly job: {job_id}",
                replace_existing=True,
                coalesce=True,
                max_instances=1,
            )

            self.jobs[job_id] = {
                "status": "active",
                "created_at": datetime.now(),
                "last_run": None,
                "next_run": job.next_run_time,
            }

            logger.info(f"Added hourly job: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}")
            raise

    def add_custom_interval_job(
        self,
        job_id: str,
        func: Callable,
        interval_minutes: int,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
    ) -> str:
        """
        Add a job that runs at custom intervals.

        Args:
            job_id: Unique job identifier
            func: Async function to execute
            interval_minutes: Interval in minutes
            args: Function positional arguments
            kwargs: Function keyword arguments

        Returns:
            Job ID
        """
        if kwargs is None:
            kwargs = {}

        try:
            job = self.scheduler.add_job(
                func,
                IntervalTrigger(minutes=interval_minutes),
                args=args,
                kwargs=kwargs,
                id=job_id,
                name=f"Custom interval job: {job_id}",
                replace_existing=True,
                coalesce=True,
                max_instances=1,
            )

            self.jobs[job_id] = {
                "status": "active",
                "created_at": datetime.now(),
                "last_run": None,
                "next_run": job.next_run_time,
            }

            logger.info(f"Added custom interval job: {job_id} (every {interval_minutes}m)")
            return job_id

        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}")
            raise

    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.

        Args:
            job_id: Job identifier

        Returns:
            True if removed successfully
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "removed"
            logger.info(f"Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False

    def pause_job(self, job_id: str) -> bool:
        """
        Pause a scheduled job.

        Args:
            job_id: Job identifier

        Returns:
            True if paused successfully
        """
        try:
            self.scheduler.pause_job(job_id)
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "paused"
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """
        Resume a paused job.

        Args:
            job_id: Job identifier

        Returns:
            True if resumed successfully
        """
        try:
            self.scheduler.resume_job(job_id)
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "active"
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get the status of a job.

        Args:
            job_id: Job identifier

        Returns:
            Job status dictionary or None
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                "job_id": job_id,
                "status": self.jobs.get(job_id, {}).get("status", "unknown"),
                "next_run": job.next_run_time,
                "created_at": self.jobs.get(job_id, {}).get("created_at"),
            }
        return None

    def get_all_jobs(self) -> Dict[str, Any]:
        """
        Get status of all scheduled jobs.

        Returns:
            Dictionary with all jobs and their statuses
        """
        all_jobs = {}
        for job in self.scheduler.get_jobs():
            all_jobs[job.id] = {
                "name": job.name,
                "next_run": job.next_run_time,
                "status": self.jobs.get(job.id, {}).get("status", "unknown"),
            }
        return all_jobs
