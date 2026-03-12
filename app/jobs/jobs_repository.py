# app/repositories/job_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.models.job import Job
from app.utils.category_config import SUB_CATEGORY_NAMES
from app.models.skill import SkillCategory


class JobRepository:

    def get_by_external_id(self, db: Session, external_id: str):
        return db.query(Job).filter(Job.external_id == external_id).first()

    def get_by_id(self, db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    def get_all(
        self, 
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        sub_category: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        location: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
    ):
        query = db.query(Job)

        if search:
            query = query.filter(
                or_(
                    Job.title.ilike(f"%{search}%"),
                    Job.company_name.ilike(f"%{search}%")
                )
            )
        if sub_category:
            query = (
                query.join(SkillCategory, Job.sub_category_id == SkillCategory.id)
                     .filter(SkillCategory.name == sub_category)
            )
        if job_type:
            query = query.filter(Job.job_type == job_type)
        if experience_level:
            query = query.filter(Job.experience_level == experience_level)
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if salary_min is not None:
            query = query.filter(Job.salary_min >= salary_min)
        if salary_max is not None:
            query = query.filter(Job.salary_max <= salary_max)

        total = query.count()
        jobs = query.order_by(Job.posted_date.desc()).offset(skip).limit(limit).all()
        return jobs, total

    def create(self, db: Session, job_data: dict):
        job = Job(**job_data)
        db.add(job)
        db.flush()      
        db.refresh(job)
        return job

    def update(self, db: Session, job_id: int, updates: dict):
        db.query(Job).filter(Job.id == job_id).update(
            updates, 
            synchronize_session="fetch"  
        )

    def delete(self, db: Session, job: Job):
        db.delete(job)

    def get_sub_categories(self, db: Session):
        return SUB_CATEGORY_NAMES
