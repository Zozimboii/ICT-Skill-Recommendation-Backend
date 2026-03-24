# app/admin/admin.service.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.job import Job, JobSkill
from app.models.skill import Skill

from app.models.transcript import Transcript
from app.admin.admin_schema import (
    AdminStats,
    AdminUserItem,
    AdminUserUpdate,
    AdminJobItem,
    AdminSkillItem,
    AdminSkillCreate,
    ScrapeResponse,
)

class AdminService:

    def get_stats(self, db: Session) -> AdminStats:
        return AdminStats(
            total_users=db.query(User).count(),
            total_jobs=db.query(Job).count(),
            total_skills=db.query(Skill).count(),
            total_transcripts=db.query(Transcript).count(),
        )


    def list_users(self, db: Session ,skip: int = 0, limit: int = 50) -> list[AdminUserItem]:
        users = db.query(User).offset(skip).limit(limit).all()
        return [AdminUserItem.model_validate(u) for u in users]


    def update_user(self, db: Session, user_id: int, data: AdminUserUpdate) -> AdminUserItem | None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if data.is_active is not None:
            user.is_active = data.is_active
        if data.role is not None:
            user.role = data.role
        db.commit()
        db.refresh(user)
        return AdminUserItem.model_validate(user)

    def delete_user(self, db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True

    def list_jobs(
        self,
        db: Session,
        keyword: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AdminJobItem], int]:
        q = db.query(Job)
        if keyword:
            q = q.filter(Job.title.ilike(f"%{keyword}%"))

        total = q.count()
        jobs = q.order_by(Job.id.desc()).offset(skip).limit(limit).all()

        result = []
        for job in jobs:
            skill_count = (
                db.query(func.count(JobSkill.skill_id))
                .filter(JobSkill.job_id == job.id)
                .scalar()
            ) or 0

            # sub_category_id เป็น FK → SkillCategory object ดึง .name ออกมา
            sub_cat_name: str | None = None
            if job.sub_category_id and job.sub_category:
                sub_cat_name = job.sub_category.name  # relationship → SkillCategory.name
            result.append(
                AdminJobItem(
                    id=job.id,
                    title=job.title,
                    company_name=job.company_name,
                    location=job.location,
                    sub_category=sub_cat_name, 
                    posted_date=str(job.posted_date) if job.posted_date else None,
                    skill_count=skill_count,
                )
            )

        return result, total


    def delete_job(self, db: Session, job_id: int) -> bool:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True


    def list_skills(self, db: Session, skip: int = 0, limit: int = 100) -> list[AdminSkillItem]:
        skills = db.query(Skill).offset(skip).limit(limit).all()
        result = []
        for skill in skills:
            job_count = (
                db.query(func.count(JobSkill.job_id))
                .filter(JobSkill.skill_id == skill.id)
                .scalar()
            ) or 0
            result.append(
                AdminSkillItem(
                    id=skill.id,
                    name=skill.name,
                    skill_type=skill.skill_type,
                    job_count=job_count,
                )
            )
        return result


    def create_skill(self, db: Session, data: AdminSkillCreate) -> AdminSkillItem:
        existing = db.query(Skill).filter(Skill.name == data.name.lower().strip()).first()
        if existing:
            raise ValueError(f"Skill '{data.name}' already exists")

        skill = Skill(name=data.name.lower().strip(), skill_type=data.skill_type)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return AdminSkillItem(id=skill.id, name=skill.name, skill_type=skill.skill_type, job_count=0)


    def delete_skill(self, db: Session, skill_id: int) -> bool:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return False
        db.delete(skill)
        db.commit()
        return True