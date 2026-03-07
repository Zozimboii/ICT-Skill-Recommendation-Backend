# backend/app/api/v1/jobs.py
# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.orm import Session

# from app.db.database import get_db
# from app.services.jobs_service import list_jobs, search_jobs
# from app.db.models import JobPosting

# router = APIRouter()


# @router.get("/")
# def get_jobs(db: Session = Depends(get_db)):
#     # GET /api/v1/jobs
#     return list_jobs(db)


# @router.get("/searchjobs")
# def get_searchjobs(
#     q: str = Query(..., min_length=1),
#     limit: int = Query(20, ge=1, le=100),
#     db: Session = Depends(get_db),
# ):
#     # GET /api/v1/jobs/searchjobs?q=...&limit=20
#     return search_jobs(db, q=q, limit=limit)


# @router.get("/by-skill")
# def get_jobs_by_skill(skill: str, db: Session = Depends(get_db)):
#     results = (
#         db.query(JobPosting)
#         .filter(JobPosting.description.ilike(f"%{skill}%"))
#         .limit(20)
#         .all()
#     )

#     return {
#         "jobs": [
#             {
#                 "id": j.id,
#                 "title": j.title,
#                 "link": j.link,
#                 "sub_category": j.sub_category_name,
#             }
#             for j in results
#         ]
#     }


from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.core.database import get_db
# from app.db.models import JobPosting, JobSkill, JobSnapshot
from app.schemas.search import SearchJobSummary
from app.model.job import Job, JobSkill
from app.schemas.jobs import JobListResponse, JobOut
from app.services.jobs.jobs_service import JobService


router = APIRouter()


# @router.get("/")
# def get_jobs(
#     sub_category_id: int | None = None,
#     skill_name: str | None = None,
#     db: Session = Depends(get_db)
# ):
#     query = db.query(JobPosting)

#     if sub_category_id:
#         query = query.filter(JobPosting.sub_category_id == sub_category_id)

#     if skill_name:
#         query = (
#             query.join(JobSkill, JobSkill.job_id == JobPosting.job_id)
#             .filter(JobSkill.skill_name == skill_name)
#         )

#     jobs = query.limit(50).all()
# @router.get("/")
# def get_jobs(
#     sub_category_id: int | None = None,
#     keyword: str | None = None,
#     skill_name: str | None = None,
#     db: Session = Depends(get_db)
# ):
#     query = db.query(Job)

#     if sub_category_id:
#         query = query.filter(Job.sub_category_id == sub_category_id)

#     if keyword:
#         query = query.filter(Job.title.ilike(f"%{keyword}%"))

#     if skill_name:
#         query = (
#             query.join(JobSkill, JobSkill.job_id == Job.job_id)
#             .filter(JobSkill.skill_name == skill_name)
#         )

#     jobs = query.limit(50).all()
#     return [
#         {
#             "id": job.id,
#             "job_title": job.title,
#             "description": job.description,
#             "posted_date": job.posted_date,
#             "location": "Bangkok",  # ถ้ายังไม่มี field
#             "sub_category_id": job.sub_category_id,
#             "sub_category_name": job.sub_category_name,
#             "hard_skills": [
#                 {
#                     "skill_name": s.skill_name
#                 }
#                 for s in job.skills
#                 if s.skill_type == "hard_skill"
#             ]
#         }
#         for job in jobs
#     ]


# @router.get("/meta")
# def get_meta(db: Session = Depends(get_db)):
#     min_date = db.query(func.min(JobPosting.snapshot_date)).scalar()
#     max_date = db.query(func.max(JobPosting.snapshot_date)).scalar()

#     return {
#         "min_snapshot_date": min_date,
#         "max_snapshot_date": max_date,
#     }


# @router.get("/options")
# def get_job_options(db: Session = Depends(get_db)):

#     rows = (
#         db.query(
#             JobSnapshot.sub_category_id,
#             JobSnapshot.sub_category_name
#         )
#         .distinct()
#         .order_by(JobSnapshot.sub_category_name)
#         .all()
#     )

#     return [
#         {
#             "label": row.sub_category_name,
#             "value": row.sub_category_id   # ✅ ใช้ id จริง
#         }
#         for row in rows if row.sub_category_name
#     ]
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return JobService(db).get_sub_categories()


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
    jobs, total = JobService(db).search_paginated(
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
        "data": [JobService.serialize_job(j) for j in jobs],
    }


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = JobService(db).get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobService.serialize_job(job)