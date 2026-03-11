# app/services/jobs/trend_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.job import Job, JobSkill
from app.models.skill import Skill, SkillCategory


class TrendService:

    def __init__(self, db: Session):
        self.db = db

    def get_job_trend(self):
        results = (
            self.db.query(
                SkillCategory.id.label("sub_category_id"),
                SkillCategory.name.label("sub_category"),
                func.count(Job.id).label("job_count"),
            )
            .join(SkillCategory, Job.sub_category_id == SkillCategory.id)
            .filter(Job.sub_category_id.isnot(None))
            .group_by(SkillCategory.id, SkillCategory.name)
            .order_by(func.count(Job.id).desc())
            .all()
        )
        return [
            {
                "sub_category_id": r.sub_category_id,
                "sub_category":    r.sub_category,
                "job_count":       r.job_count,
            }
            for r in results
        ]

    def get_skill_trend(self, limit: int = 20, skill_type: str | None = None):
        query = (
            self.db.query(
                Skill.id,
                Skill.name,
                Skill.skill_type,
                func.count(JobSkill.job_id).label("count"),
            )
            .join(JobSkill, Skill.id == JobSkill.skill_id)
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
                "skill":      r.name,
                "skill_type": r.skill_type,
                "count":      r.count,
            }
            for r in results
        ]

    def get_cross_data(self, sub_category: str = None, skill_id: int = None):
        if sub_category:

            results = (
                self.db.query(
                    Skill.name.label("skill"),
                    func.count(JobSkill.job_id).label("count"),
                )
                .join(JobSkill, Skill.id == JobSkill.skill_id)
                .join(Job, Job.id == JobSkill.job_id)
                .join(SkillCategory, Job.sub_category_id == SkillCategory.id)  
                .filter(SkillCategory.name == sub_category)                  
                .group_by(Skill.name)
                .order_by(func.count(JobSkill.job_id).desc())
                .limit(10)
                .all()
            )
            return {
                "filter": {"sub_category": sub_category},
                "type":   "skills_by_category",
                "data":   [{"skill": r.skill, "count": r.count} for r in results],
            }

        if skill_id:

            results = (
                self.db.query(
                    SkillCategory.name.label("sub_category"),       
                    func.count(Job.id).label("job_count"),
                )
                .join(JobSkill, Job.id == JobSkill.job_id)
                .join(SkillCategory, Job.sub_category_id == SkillCategory.id)  
                .filter(JobSkill.skill_id == skill_id)
                .filter(Job.sub_category_id.isnot(None))
                .group_by(SkillCategory.id, SkillCategory.name)
                .order_by(func.count(Job.id).desc())
                .all()
            )
            return {
                "filter": {"skill_id": skill_id},
                "type":   "categories_by_skill",
                "data":   [{"sub_category": r.sub_category, "job_count": r.job_count} for r in results],
            }

        return {
            "filter":      None,
            "type":        "overview",
            "job_trend":   self.get_job_trend(),
            "skill_trend": self.get_skill_trend(limit=10),
        }

    def get_jobs_by_skill(self, skill_id: int, limit: int = 20):
        results = (
            self.db.query(
                Job.id,
                Job.title,
                Job.company_name,
                SkillCategory.name.label("sub_category"),
            )
            .join(JobSkill, Job.id == JobSkill.job_id)
            .join(SkillCategory, Job.sub_category_id == SkillCategory.id, isouter=True)
            .filter(JobSkill.skill_id == skill_id)
            .limit(limit)
            .all()
        )

        return [
            {
                "id":           r.id,
                "title":        r.title,
                "sub_category": r.sub_category,
                "company":      r.company_name,
            }
            for r in results
        ]

    def get_sankey_data(self, top_categories: int = 8, top_skills_per_cat: int = 4):
        """
        Returns sankey links: sub_category → skill → weight
        weight = จำนวน job ที่มีทั้ง sub_category นั้น และ skill นั้น
        """

        top_cats = (
            self.db.query(
                SkillCategory.id,
                SkillCategory.name,
                func.count(Job.id).label("job_count"),
            )
            .join(Job, Job.sub_category_id == SkillCategory.id)
            .filter(Job.sub_category_id.isnot(None))
            .group_by(SkillCategory.id, SkillCategory.name)
            .order_by(func.count(Job.id).desc())
            .limit(top_categories)
            .all()
            
        )

        top_cat_ids = [r.id for r in top_cats]

        results = (
            self.db.query(
                SkillCategory.name.label("sub_category"),
                Skill.name.label("skill"),
                Skill.skill_type,
                func.count(Job.id).label("weight"),
            )
            .join(Job, Job.sub_category_id == SkillCategory.id)
            .join(JobSkill, JobSkill.job_id == Job.id)
            .join(Skill, Skill.id == JobSkill.skill_id)
            .filter(SkillCategory.id.in_(top_cat_ids))
            .filter(Skill.skill_type == "hard_skill")  
            .group_by(SkillCategory.name, Skill.name, Skill.skill_type)
            .order_by(SkillCategory.name, func.count(Job.id).desc())
            .all()
            
        )

        from collections import defaultdict
        cat_skill_counts = defaultdict(list)
        for r in results:
            cat_skill_counts[r.sub_category].append({
                "from": r.sub_category,
                "to": r.skill,
                "weight": int(r.weight),
            })

        links = []
        for cat, skills in cat_skill_counts.items():
            top = sorted(skills, key=lambda x: x["weight"], reverse=True)[:top_skills_per_cat]
            links.extend(top)

        return links