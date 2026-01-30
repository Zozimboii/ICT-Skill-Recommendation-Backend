# backend/app/api/v1/jobs.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.jobs_service import list_jobs, search_jobs

router = APIRouter()


@router.get("")
def get_jobs(db: Session = Depends(get_db)):
    # GET /api/v1/jobs
    return list_jobs(db)


@router.get("/searchjobs")
def get_searchjobs(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # GET /api/v1/jobs/searchjobs?q=...&limit=20
    return search_jobs(db, q=q, limit=limit)
