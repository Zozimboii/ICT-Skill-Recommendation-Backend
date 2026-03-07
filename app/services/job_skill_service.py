# app/services/job_skill_service.py


from app.model.job import JobSkill


class JobSkillService:

    def attach_skill_to_job(
        self, db, job_id: int, skill_id: int, score: float = 1.0
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
        
        

        return relation
    
        # ============================================================
    # เพิ่มใน app/services/job_skill_service.py
    # ============================================================

    def count_skills_for_job(self, db, job_id: int) -> int:
        # """นับจำนวน skill ที่ผูกกับ job นี้ (ใช้เช็คว่าต้อง re-extract ไหม)"""
        return db.query(JobSkill).filter(JobSkill.job_id == job_id).count()