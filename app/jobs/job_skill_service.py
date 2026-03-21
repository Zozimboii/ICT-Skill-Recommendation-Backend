# # # app/services/job_skill_service.py


# from app.models.job import Job, JobSkill
# from app.models.skill import Skill
# from app.utils.job_importance import SCORE_HARD_SKILL, calc_importance_score

# class JobSkillService:

#     def attach_skill_to_job(
#         self,
#         db,
#         job_id: int,
#         skill_id: int,
#         score: float = SCORE_HARD_SKILL   # default = 2.0
#     ):
#         exists = db.query(JobSkill).filter(
#             JobSkill.job_id == job_id,
#             JobSkill.skill_id == skill_id
#         ).first()

#         if exists:
#             return exists

#         relation = JobSkill(
#             job_id=job_id,
#             skill_id=skill_id,
#             importance_score=score
#         )
#         db.add(relation)
#         db.flush()
#         return relation

#     def attach_skill_with_auto_score(
#         self,
#         db,
#         job: Job,
#         skill: Skill,
#         mention_count: int = 1
#     ):
#         """
#         attach skill พร้อมคำนวณ importance_score อัตโนมัติ
#         ใช้แทน attach_skill_to_job ใน scraper
#         """
#         score = calc_importance_score(job, skill, mention_count)
#         return self.attach_skill_to_job(db, job.id, skill.id, score)

#     def count_skills_for_job(self, db, job_id: int) -> int:
#         return db.query(JobSkill).filter(JobSkill.job_id == job_id).count()
# app/jobs/job_skill_service.py  (v2)
# เพิ่ม attach_skill_with_score ที่รับ importance_score โดยตรง

from app.models.job import Job, JobSkill
from app.models.skill import Skill
from app.utils.job_importance import SCORE_HARD_SKILL, calc_importance_score


class JobSkillService:

    def attach_skill_to_job(
        self,
        db,
        job_id: int,
        skill_id: int,
        score: float = SCORE_HARD_SKILL,
    ):
        """attach skill พร้อม score — upsert (ไม่ duplicate)"""
        exists = db.query(JobSkill).filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill_id,
        ).first()

        if exists:
            # เลือก score สูงกว่า
            if score > (exists.importance_score or 0):
                exists.importance_score = score
            return exists

        relation = JobSkill(job_id=job_id, skill_id=skill_id, importance_score=score)
        db.add(relation)
        db.flush()
        return relation

    def attach_skill_with_score(
        self,
        db,
        job: Job,
        skill: Skill,
        importance_score: float,
    ):
        """
        ← ใหม่: รับ importance_score จาก structured extractor โดยตรง
        (Required=4.0, Preferred=2.0, Mentioned=0.8)
        """
        return self.attach_skill_to_job(db, job.id, skill.id, importance_score)

    def attach_skill_with_auto_score(
        self,
        db,
        job: Job,
        skill: Skill,
        mention_count: int = 1,
    ):
        """
        Legacy — คำนวณ score จาก job title + mention_count
        ใช้เมื่อไม่มี structured extraction
        """
        score = calc_importance_score(job, skill, mention_count)
        return self.attach_skill_to_job(db, job.id, skill.id, score)

    def count_skills_for_job(self, db, job_id: int) -> int:
        return db.query(JobSkill).filter(JobSkill.job_id == job_id).count()