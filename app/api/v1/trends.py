from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
# from app.services.trends_service import get_jobsdb_trend, get_skills_trend
from app.services.jobs.trend_service import TrendService
from app.services.jobs.skills_service import SkillService


router = APIRouter()


# @router.get("/jobsdb")
# def job_trend(days: int = Query(60), db: Session = Depends(get_db)):
#     return get_jobsdb_trend(db, days)


# @router.get("/skills")
# def skill_trend(days: int = Query(60), db: Session = Depends(get_db)):
#     return get_skills_trend(db, days)


@router.get("/jobs")
def get_job_trend(db: Session = Depends(get_db)):
    """Return job count grouped by sub_category."""
    return TrendService(db).get_job_trend()


@router.get("/skills")
def get_skill_trend(
    limit: int = Query(20, ge=1, le=100),
     skill_type: Optional[str] = Query(
        None,
        description="Filter by skill type (hard_skill / soft_skill)"
    ),
    db: Session = Depends(get_db),
):
    """Return top skills ranked by job demand."""
    return TrendService(db).get_skill_trend(limit=limit,skill_type=skill_type,)


@router.get("/cross")
def get_cross_data(
    sub_category: Optional[str] = Query(None, description="Filter by job sub-category"),
    skill_id: Optional[int] = Query(None, description="Filter by skill ID"),
    db: Session = Depends(get_db),
):
    """
    Dynamic cross-filter endpoint for graph interaction.
    - ?sub_category=Backend  → skills breakdown for that category
    - ?skill_id=5            → job categories that need that skill
    - (no filter)            → overview of both job trend + skill trend
    """
    return TrendService(db).get_cross_data(sub_category=sub_category, skill_id=skill_id)


@router.get("/skills/by-category")
def get_skills_by_category(
    sub_category: str = Query(..., description="Job sub-category name"),
    limit: int = Query(10, ge=1, le=50),
    skill_type: str | None = None,
    db: Session = Depends(get_db),
):
    service = SkillService(db)
    return service.get_skills_by_category(
        sub_category,
        limit,
        skill_type
    )
@router.get("/jobs-by-skill")
def get_jobs_by_skill(skill_id: int, limit: int = 20, db: Session = Depends(get_db)):
    service = TrendService(db)
    return service.get_jobs_by_skill(skill_id, limit)

# เพิ่มใน app/api/v1/trends.py

@router.get("/sankey")
def get_sankey(
    top_categories: int = 10,
    top_skills: int = 6,
    db: Session = Depends(get_db),
):
    """
    Returns sankey links for sub_category → skill visualization.
    Response: [{ "from": "Developers/Programmers", "to": "Python", "weight": 120 }]
    """
    return TrendService(db).get_sankey_data(
        top_categories=top_categories,
        top_skills_per_cat=top_skills,
    )