# เพิ่มใน app/api/v1/trends.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.jobs.skill_query_service import SkillService
from app.trends.trends_service import TrendService



router = APIRouter()
trend_service = TrendService()
skill_service = SkillService()
@router.get("/jobs")
def get_job_trend(db: Session = Depends(get_db)):
    """Return job count grouped by sub_category."""
    return trend_service.get_job_trend(db)


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
    return trend_service.get_skill_trend(db,limit=limit,skill_type=skill_type,)


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
    return trend_service.get_cross_data(db,sub_category=sub_category, skill_id=skill_id)


@router.get("/skills/by-category")
def get_skills_by_category(
    sub_category: str = Query(..., description="Job sub-category name"),
    limit: int = Query(10, ge=1, le=50),
    skill_type: str | None = None,
    db: Session = Depends(get_db),
):
    return skill_service.get_skills_by_category(
        db,
        sub_category,
        limit,
        skill_type
    )
@router.get("/jobs-by-skill")
def get_jobs_by_skill(skill_id: int, limit: int = 20, db: Session = Depends(get_db)):
    return trend_service.get_jobs_by_skill(db,skill_id, limit)


@router.get("/sankey")
def get_sankey(
    top_categories: int = 10,
    top_skills: int = 6,
    db: Session = Depends(get_db),
):
    return trend_service.get_sankey_data(
        db,
        top_categories=top_categories,
        top_skills_per_cat=top_skills,
    )