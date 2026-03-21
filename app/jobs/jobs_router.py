# backend/app/api/v1/jobs.py
# ข้อ 4: เพิ่ม min_date / max_date filter + date_range endpoint

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job
from app.jobs.jobs_schema import JobListResponse, JobOut
from app.jobs.jobs_service import JobService


router = APIRouter()
job_service = JobService()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return job_service.get_sub_categories(db)


# ── ข้อ 4: date range endpoint ────────────────────────────────────────────────
@router.get("/date-range")
def get_date_range(db: Session = Depends(get_db)):
    """
    Return min_date / max_date ของ jobs ใน DB
    Frontend ใช้ตั้ง default range ของ date filter
    """
    row = db.query(
        func.min(Job.posted_date).label("min_date"),
        func.max(Job.posted_date).label("max_date"),
    ).first()

    return {
        "min_date": str(row.min_date) if row.min_date else None,
        "max_date": str(row.max_date) if row.max_date else None,
    }


@router.get("/search", response_model=JobListResponse)
def search_jobs(
    keyword:          Optional[str]  = Query(None),
    sub_category:     Optional[str]  = Query(None),
    job_type:         Optional[str]  = Query(None),
    experience_level: Optional[str]  = Query(None),
    search_by:        Optional[str]  = Query(None, description="title | skill | None(all)"),
    min_date:         Optional[date] = Query(None, description="กรองงานตั้งแต่วันที่ (YYYY-MM-DD)"),
    max_date:         Optional[date] = Query(None, description="กรองงานถึงวันที่ (YYYY-MM-DD)"),
    page:             int            = Query(1, ge=1),
    limit:            int            = Query(20, ge=1, le=100),
    db:               Session        = Depends(get_db),
):
    jobs, total = job_service.search_paginated(
        db,
        keyword=keyword,
        sub_category=sub_category,
        job_type=job_type,
        experience_level=experience_level,
        search_by=search_by,
        min_date=min_date,
        max_date=max_date,
        page=page,
        limit=limit,
    )
    return {
        "total": total,
        "page":  page,
        "limit": limit,
        "data":  [job_service.serialize_job(j) for j in jobs],
    }


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_service.serialize_job(job)