# backend/app/api/v1/jobs.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job, JobSkill
from app.jobs.jobs_schema import JobListResponse, JobOut
from app.jobs.jobs_service import JobService


router = APIRouter()
job_service = JobService()

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return job_service.get_sub_categories(db)


@router.get("/search", response_model=JobListResponse)
def search_jobs(
    keyword: Optional[str] = Query(None),
    sub_category: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    jobs, total = job_service.search_paginated(
        db,
        keyword=keyword,
        sub_category=sub_category,
        job_type=job_type,
        experience_level=experience_level,
        page=page,
        limit=limit,
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [job_service.serialize_job(j) for j in jobs],
    }


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_service.serialize_job(db,job)