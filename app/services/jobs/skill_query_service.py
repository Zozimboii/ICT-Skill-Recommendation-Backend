# app/services/jobs/skills_service.py  (api version)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.model.job import Job, JobSkill
from app.model.skill import Skill, SkillCategory  # ✅ เพิ่ม SkillCategory


class SkillService:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Skill).order_by(Skill.name).all()

    def get_top10(self):
        results = (
            self.db.query(
                Skill.id,
                Skill.name,
                func.count(JobSkill.job_id).label("job_count"),
            )
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .group_by(Skill.id, Skill.name)
            .order_by(func.count(JobSkill.job_id).desc())
            .limit(10)
            .all()
        )
        return [{"id": r.id, "name": r.name, "job_count": r.job_count} for r in results]

    def get_by_id(self, skill_id: int):
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def create(self, payload: dict):
        skill = Skill(**payload)
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def update(self, skill_id: int, payload: dict):
        skill = self.get_by_id(skill_id)
        if not skill:
            return None
        for key, value in payload.items():
            setattr(skill, key, value)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def delete(self, skill_id: int):
        skill = self.get_by_id(skill_id)
        if not skill:
            return False
        self.db.delete(skill)
        self.db.commit()
        return True

    def get_skills_by_category(
        self,
        sub_category_name: str,
        limit: int = 10,
        skill_type: str | None = None,
    ):
        query = (
            self.db.query(
                Skill.id,
                Skill.name,
                Skill.skill_type,
                func.count(JobSkill.job_id).label("job_count"),
            )
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .join(Job, Job.id == JobSkill.job_id)
            .join(SkillCategory, Job.sub_category_id == SkillCategory.id)  # ✅
            .filter(SkillCategory.name == sub_category_name)               # ✅
            .group_by(Skill.id, Skill.name, Skill.skill_type)
        )

        if skill_type:
            query = query.filter(Skill.skill_type == skill_type)

        results = (
            query.order_by(func.count(JobSkill.job_id).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id":         r.id,
                "name":       r.name,
                "skill_type": r.skill_type,
                "job_count":  r.job_count,
            }
            for r in results
        ]