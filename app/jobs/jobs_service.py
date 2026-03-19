# app/services/jobs/jobs_service.py  (api version)

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional

from app.models.job import Job, JobSkill
from app.models.skill import Skill, SkillCategory  # ✅ เพิ่ม SkillCategory


class JobService:

    def get_all(self, db: Session, filters: dict = None):
        q = db.query(Job)
        if filters:
            if filters.get("sub_category"):
                q = (
                    q.join(SkillCategory, Job.sub_category_id == SkillCategory.id)
                     .filter(SkillCategory.name == filters["sub_category"])  # ✅
                )
        return q.order_by(Job.id.desc()).all()
    
    def get_by_id(self, db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    def create(self, db: Session, payload: dict):
        job = Job(**payload)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def update(self, db: Session, job_id: int, payload: dict):
        job = self.get_by_id(db,job_id)
        if not job:
            return None
        for key, value in payload.items():
            setattr(job, key, value)
        db.commit()
        db.refresh(job)
        return job

    def delete(self, db: Session, job_id: int):
        job = self.get_by_id(db,job_id)
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True

    def get_jobs_by_skill(self, db: Session, skill_id: int):
        return (
            db.query(Job)
            .join(JobSkill, Job.id == JobSkill.job_id)
            .filter(JobSkill.skill_id == skill_id)
            .all()
        )

    def search(self, db: Session, keyword: str, sub_category: str = None):
        q = db.query(Job).filter(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.description.ilike(f"%{keyword}%"),
            )
        )
        if sub_category:
            q = (
                q.join(SkillCategory, Job.sub_category_id == SkillCategory.id)
                 .filter(SkillCategory.name == sub_category)  # ✅
            )
        return q.all()

    def search_paginated(
        self,
        db: Session,
        keyword: Optional[str] = None,
        sub_category: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Job], int]:

        q = db.query(Job).options(
            joinedload(Job.skills).joinedload(JobSkill.skill)
        )

        # ✅ JOIN skill (สำคัญมาก)
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
                        Skill.name.ilike(kw),  # 🔥 ใช้ได้แล้ว
                    )
                 )
            )

        # ✅ filter อื่น
        if sub_category and sub_category != "all":
            q = (
                q.join(SkillCategory, Job.sub_category_id == SkillCategory.id)
                 .filter(SkillCategory.name == sub_category)
            )

        if job_type and job_type != "all":
            q = q.filter(Job.job_type == job_type)

        if experience_level and experience_level != "all":
            q = q.filter(Job.experience_level == experience_level)

        # ✅ กัน duplicate (สำคัญ)
        q = q.distinct()

        # ✅ total ต้องนับหลัง filter ทั้งหมด
        total = q.count()

        jobs = (
            q.order_by(Job.posted_date.desc())
             .offset((page - 1) * limit)
             .limit(limit)
             .all()
        )

        return jobs, total

    def get_sub_categories(self, db: Session) -> list[str]:
        # ✅ ดึงจาก SkillCategory โดยตรง ไม่ต้อง distinct จาก Job อีกต่อไป
        from app.utils.category_config import SUB_CATEGORY_NAMES
        return SUB_CATEGORY_NAMES

    @staticmethod
    def serialize_job(job: Job) -> dict:
        # ✅ sub_category ดึงจาก relationship
        sub_cat_name = job.sub_category.name if job.sub_category else None

        return {
            "id":               job.id,
            "title":            job.title,
            "company_name":     job.company_name,
            "location":         job.location,
            "description":      job.description,
            "sub_category":     sub_cat_name,        # ✅
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
                for js in job.skills
                if js.skill
            ],
        }