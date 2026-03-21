# app/services/jobs/jobs_service.py
# ข้อ 4: เพิ่ม min_date / max_date ใน search_paginated

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.job import Job, JobSkill
from app.models.skill import Skill, SkillCategory


class JobService:

    def get_all(self, db: Session, filters: dict = None):
        q = db.query(Job)
        if filters:
            if filters.get("sub_category"):
                q = (
                    q.join(SkillCategory, Job.sub_category_id == SkillCategory.id)
                     .filter(SkillCategory.name == filters["sub_category"])
                )
        return q.order_by(Job.id.desc()).all()

    def get_by_id(self, db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    def search_paginated(
        self,
        db: Session,
        keyword:          Optional[str]  = None,
        sub_category:     Optional[str]  = None,
        job_type:         Optional[str]  = None,
        experience_level: Optional[str]  = None,
        # ── ข้อ 4: date range ────────────────────────────────────
        min_date:         Optional[date] = None,
        max_date:         Optional[date] = None,
        page:             int = 1,
        limit:            int = 20,
    ) -> tuple[list[Job], int]:

        q = db.query(Job).options(
            joinedload(Job.skills).joinedload(JobSkill.skill)
        )

        # keyword → title + company + skill name
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            q = (
                q.outerjoin(JobSkill, Job.id == JobSkill.job_id)
                 .outerjoin(Skill, JobSkill.skill_id == Skill.id)
                 .filter(
                    or_(
                        Job.title.ilike(kw),
                        Job.company_name.ilike(kw),
                        Job.description.ilike(kw),
                        Skill.name.ilike(kw),
                    )
                 )
            )

        # sub_category dropdown
        if sub_category and sub_category != "all":
            q = (
                q.join(SkillCategory, Job.sub_category_id == SkillCategory.id)
                 .filter(SkillCategory.name == sub_category)
            )

        # optional filters
        if job_type and job_type != "all":
            q = q.filter(Job.job_type == job_type)
        if experience_level and experience_level != "all":
            q = q.filter(Job.experience_level == experience_level)

        # ── ข้อ 4: date range filter ────────────────────────────
        if min_date:
            q = q.filter(Job.posted_date >= min_date)
        if max_date:
            q = q.filter(Job.posted_date <= max_date)

        q = q.distinct()
        total = q.count()
        jobs  = (
            q.order_by(Job.posted_date.desc())
             .offset((page - 1) * limit)
             .limit(limit)
             .all()
        )
        return jobs, total

    def get_sub_categories(self, db: Session) -> list[str]:
        from app.utils.category_config import SUB_CATEGORY_NAMES
        return SUB_CATEGORY_NAMES

    @staticmethod
    def serialize_job(job: Job) -> dict:
        sub_cat_name = job.sub_category.name if job.sub_category else None
        return {
            "id":               job.id,
            "title":            job.title,
            "company_name":     job.company_name,
            "location":         job.location,
            "description":      job.description,
            "sub_category":     sub_cat_name,
            "sub_category_id":  job.sub_category_id,
            "job_type":         job.job_type,
            "experience_level": job.experience_level,
            "posted_date":      str(job.posted_date) if job.posted_date else None,
            "url":              job.url,
            "skills": [
                {
                    "id":         js.skill.id,
                    "name":       js.skill.name,
                    "skill_type": js.skill.skill_type,
                }
                for js in job.skills if js.skill
            ],
        }