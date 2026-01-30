# backend/app/api/v1/trends.py

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import JobCountHistory, JobSkillTrend

router = APIRouter()


@router.get("/jobsdb")
def get_job_trends(days: int = Query(30), db: Session = Depends(get_db)):
    limit_date = datetime.now().date() - timedelta(days=days)

    results = (
        db.query(
            JobCountHistory.snapshot_date,
            JobCountHistory.sub_category_name,
            JobCountHistory.job_count,
        )
        .filter(JobCountHistory.snapshot_date >= limit_date)
        .all()
    )

    series = [
        {
            "snapshot_date": r[0].strftime("%Y-%m-%d"),
            "sub_category_name": r[1],
            "job_count": r[2],
        }
        for r in results
    ]
    return {"series": series}


@router.get("/skills")
def get_skill_trends(days: int = Query(30), db: Session = Depends(get_db)):
    limit_date = datetime.now().date() - timedelta(days=days)

    results = (
        db.query(
            JobSkillTrend.snapshot_date, JobSkillTrend.skill_name, JobSkillTrend.count
        )
        .filter(JobSkillTrend.snapshot_date >= limit_date)
        .all()
    )

    series = [
        {
            "snapshot_date": r[0].strftime("%Y-%m-%d")
            if hasattr(r[0], "strftime")
            else str(r[0]),
            "skill_name": r[1],
            "count": r[2],
        }
        for r in results
    ]
    return {"series": series}
