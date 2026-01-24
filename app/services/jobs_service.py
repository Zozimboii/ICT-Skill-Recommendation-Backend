# backend/app/services/jobs_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import JobsSkill, JobCountBySubCategory

def list_jobs(db: Session):
    rows = (
        db.query(JobsSkill.job_id, JobsSkill.title)
        .group_by(JobsSkill.job_id, JobsSkill.title)
        .limit(50)
        .all()
    )
    return [{"job_id": r[0], "title": r[1]} for r in rows]

def search_jobs(db: Session, q: str, limit: int = 20):
    keyword = q.strip().lower()

    matches = (
        db.query(
            JobCountBySubCategory.sub_category_id,
            JobCountBySubCategory.sub_category_name,
            JobCountBySubCategory.job_count,
        )
        .filter(func.lower(JobCountBySubCategory.sub_category_name).like(f"%{keyword}%"))
        .order_by(JobCountBySubCategory.job_count.desc())
        .limit(limit)
        .all()
    )

    if not matches:
        return {
            "sub_category_id": "",
            "sub_category_name": keyword,
            "job_count": 0,
            "top_categories": [],
            "related_sub_categories": [],
        }

    main_sub_id, main_sub_name, main_job_count = matches[0]

    top_categories = (
        db.query(
            JobCountBySubCategory.main_category_id,
            JobCountBySubCategory.main_category_name,
            JobCountBySubCategory.sub_category_id,
            JobCountBySubCategory.sub_category_name,
            JobCountBySubCategory.job_count,
        )
        .filter(JobCountBySubCategory.sub_category_id == main_sub_id)
        .order_by(JobCountBySubCategory.job_count.desc())
        .all()
    )

    main_category_id = top_categories[0][0] if top_categories else None

    related = (
        db.query(
            JobCountBySubCategory.sub_category_id,
            JobCountBySubCategory.sub_category_name,
            JobCountBySubCategory.job_count,
        )
        .filter(JobCountBySubCategory.main_category_id == main_category_id)
        .filter(JobCountBySubCategory.sub_category_id != main_sub_id)
        .order_by(JobCountBySubCategory.job_count.desc())
        .limit(10)
        .all()
    )

    return {
        "sub_category_id": int(main_sub_id),
        "sub_category_name": main_sub_name,
        "job_count": int(main_job_count),
        "top_categories": [
            {
                "main_category_id": r[0],
                "main_category_name": r[1],
                "sub_category_id": r[2],
                "sub_category_name": r[3],
                "job_count": int(r[4]),
            }
            for r in top_categories
        ],
        "related_sub_categories": [
            {"sub_category_id": int(r[0]), "sub_category_name": r[1], "job_count": int(r[2])}
            for r in related
        ],
    }
