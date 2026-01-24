from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, select

from app.db.models import (
    JobsSkill,
    JobSkillCountBySkillname,
    JobSkillsWithCategories,
)

def search_skill(db: Session, keyword: str ,limit: int = 20):
    keyword = keyword.strip().lower()

    matches = (
        db.query(
            JobSkillCountBySkillname.skill_name,
            JobSkillCountBySkillname.skill_type,
            JobSkillCountBySkillname.job_skill_count.label("job_count"),
        )
        .filter(func.lower(JobSkillCountBySkillname.skill_name).like(f"%{keyword}%"))
        .order_by(JobSkillCountBySkillname.job_skill_count.desc())
        .limit(limit)
        .all()
    )

    if not matches:
        return {
            "skill_name": keyword,
            "skill_type": "",
            "job_count": 0,
            "top_subcategories": [],
            "related_skills": [],
        }

    main_skill_name, main_skill_type, main_job_count = matches[0]

    job_ids_subq = (
        db.query(JobsSkill.job_id)
        .filter(func.lower(JobsSkill.skill_name) == func.lower(main_skill_name))
        .subquery()
    )
    job_ids_select = select(job_ids_subq.c.job_id)
    top_subcategories = (
        db.query(
            JobSkillsWithCategories.main_category_id,
            JobSkillsWithCategories.main_category_name,
            JobSkillsWithCategories.sub_category_id,
            JobSkillsWithCategories.sub_category_name,
            func.count(distinct(JobSkillsWithCategories.job_id)).label("count"),
        )
        .filter(JobSkillsWithCategories.job_id.in_(job_ids_select))
        .group_by(
            JobSkillsWithCategories.main_category_id,
            JobSkillsWithCategories.main_category_name,
            JobSkillsWithCategories.sub_category_id,
            JobSkillsWithCategories.sub_category_name,
        )
        .order_by(func.count(distinct(JobSkillsWithCategories.job_id)).desc())
        .limit(10)
        .all()
    )

    related = (
        db.query(
            JobsSkill.skill_name,
            func.count(distinct(JobsSkill.job_id)).label("count"),
        )
        .filter(JobsSkill.job_id.in_(select(job_ids_subq)))
        .filter(func.lower(JobsSkill.skill_name) != func.lower(main_skill_name))
        .group_by(JobsSkill.skill_name)
        .order_by(func.count(distinct(JobsSkill.job_id)).desc())
        .limit(20)
        .all()
    )

    return {
        "skill_name": main_skill_name,
        "skill_type": main_skill_type,
        "job_count": int(main_job_count),
        "top_subcategories": [
            {
                "main_category_id": r[0],
                "main_category_name": r[1],
                "sub_category_id": r[2],
                "sub_category_name": r[3],
                "count": int(r[4]),
            }
            for r in top_subcategories
        ],
        "related_skills": [{"skill_name": r[0], "count": int(r[1])} for r in related],
    }
