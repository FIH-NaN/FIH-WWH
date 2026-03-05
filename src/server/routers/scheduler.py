"""
API endpoints for scheduler management and task execution.
Allows users to view scheduled jobs and manually trigger tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import get_current_user
from db.database import get_db
from db.db_models import User
from db.schemas import SuccessResponse
from util.scheduler import list_jobs, remove_job, get_scheduler
from util.tasks import (
    fetch_global_markets_data,
    calculate_asset_allocation_frontier,
    update_asset_valuations,
)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/jobs", response_model=SuccessResponse)
def list_scheduled_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get list of all scheduled jobs."""
    jobs = list_jobs()
    job_data = []
    
    for job in jobs:
        job_data.append({
            "id": job.id,
            "name": job.name,
            "trigger": str(job.trigger),
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        })
    
    return SuccessResponse(
        success=True,
        data={
            "jobs": job_data,
            "total": len(job_data),
        },
    )


@router.post("/jobs/{job_id}/trigger", response_model=SuccessResponse)
def manually_trigger_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually trigger a scheduled job."""
    # Map job IDs to functions
    job_functions = {
        "fetch_markets_morning": fetch_global_markets_data,
        "fetch_markets_afternoon": fetch_global_markets_data,
        "calc_allocation_frontier": calculate_asset_allocation_frontier,
        "update_valuations": update_asset_valuations,
    }
    
    if job_id not in job_functions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    
    try:
        result = job_functions[job_id]()
        return SuccessResponse(
            success=True,
            data={
                "job_id": job_id,
                "result": result,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job execution failed: {str(e)}",
        )


@router.delete("/jobs/{job_id}", response_model=SuccessResponse)
def delete_scheduled_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a scheduled job."""
    try:
        remove_job(job_id)
        return SuccessResponse(
            success=True,
            message=f"Job '{job_id}' removed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to remove job: {str(e)}",
        )


@router.get("/status", response_model=SuccessResponse)
def scheduler_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get scheduler status."""
    scheduler = get_scheduler()
    jobs = list_jobs()
    
    return SuccessResponse(
        success=True,
        data={
            "running": scheduler.running,
            "jobs_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                }
                for job in jobs
            ],
        },
    )
