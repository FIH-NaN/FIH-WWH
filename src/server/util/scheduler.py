"""
Scheduler core module using APScheduler for background task execution.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = None


def get_scheduler() -> BackgroundScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(daemon=True)
    return _scheduler


def start_scheduler():
    """Start the background scheduler."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("✓ Background task scheduler started")


def shutdown_scheduler():
    """Gracefully shutdown the scheduler."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✓ Background task scheduler shutdown")


def schedule_cron_job(
    job_func,
    job_id: str,
    hour: int,
    minute: int = 0,
    day_of_week: str = "*",
    replace_existing: bool = True,
    **kwargs
):
    """
    Schedule a job using cron-like timing.
    
    Args:
        job_func: Callable to execute
        job_id: Unique job identifier
        hour: Hour to run (0-23)
        minute: Minute to run (0-59)
        day_of_week: Day of week (0-6, 0=Monday, or name)
        replace_existing: Replace if job already exists
        **kwargs: Additional arguments to pass to job_func
    """
    scheduler = get_scheduler()
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        day_of_week=day_of_week,
    )
    scheduler.add_job(
        job_func,
        trigger=trigger,
        id=job_id,
        replace_existing=replace_existing,
        kwargs=kwargs,
        name=f"{job_id} (cron: {hour}:{minute:02d})",
    )
    logger.info(f"✓ Scheduled cron job: {job_id} at {hour}:{minute:02d}")


def schedule_interval_job(
    job_func,
    job_id: str,
    interval_minutes: int = 60,
    replace_existing: bool = True,
    **kwargs
):
    """
    Schedule a job to run at regular intervals.
    
    Args:
        job_func: Callable to execute
        job_id: Unique job identifier
        interval_minutes: Run every N minutes
        replace_existing: Replace if job already exists
        **kwargs: Additional arguments to pass to job_func
    """
    scheduler = get_scheduler()
    trigger = IntervalTrigger(minutes=interval_minutes)
    scheduler.add_job(
        job_func,
        trigger=trigger,
        id=job_id,
        replace_existing=replace_existing,
        kwargs=kwargs,
        name=f"{job_id} (interval: {interval_minutes}min)",
    )
    logger.info(f"✓ Scheduled interval job: {job_id} every {interval_minutes}min")


def list_jobs() -> list:
    """List all scheduled jobs."""
    scheduler = get_scheduler()
    return scheduler.get_jobs()


def remove_job(job_id: str):
    """Remove a scheduled job."""
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(job_id)
        logger.info(f"✓ Removed job: {job_id}")
    except Exception as e:
        logger.error(f"✗ Failed to remove job {job_id}: {e}")
