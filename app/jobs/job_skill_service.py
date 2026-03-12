# # app/services/job_skill_service.py


from app.models.job import Job, JobSkill
from app.models.skill import Skill
from app.utils.job_importance import SCORE_HARD_SKILL, calc_importance_score

class JobSkillService:

    def attach_skill_to_job(
        self,
        db,
        job_id: int,
        skill_id: int,
        score: float = SCORE_HARD_SKILL   # default = 2.0
    ):
        exists = db.query(JobSkill).filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id
        ).first()

        if exists:
            return exists

        relation = JobSkill(
            job_id=job_id,
            skill_id=skill_id,
            importance_score=score
        )
        db.add(relation)
        db.flush()
        return relation

    def attach_skill_with_auto_score(
        self,
        db,
        job: Job,
        skill: Skill,
        mention_count: int = 1
    ):
        """
        attach skill พร้อมคำนวณ importance_score อัตโนมัติ
        ใช้แทน attach_skill_to_job ใน scraper
        """
        score = calc_importance_score(job, skill, mention_count)
        return self.attach_skill_to_job(db, job.id, skill.id, score)

    def count_skills_for_job(self, db, job_id: int) -> int:
        return db.query(JobSkill).filter(JobSkill.job_id == job_id).count()