# # app/services/job_skill_service.py


from app.models.job import Job, JobSkill
from app.models.skill import Skill


# ── Importance score constants ────────────────────────────────────────────────
SCORE_MUST_HAVE  = 4.0   # skill ตรงกับ job title โดยตรง (เช่น Go ใน Go Developer)
SCORE_HARD_SKILL = 2.0   # hard skill ทั่วไป
SCORE_SOFT_SKILL = 1.0   # soft skill / interpersonal
SCORE_NICE_HAVE  = 0.5   # mention น้อย / ทักษะเสริม


def calc_importance_score(
    job: Job,
    skill: Skill,
    mention_count: int = 1,
) -> float:
    """
    คำนวณ importance_score ของ skill สำหรับ job นี้

    Rules (เรียงลำดับ priority):
    1. Must-have  → skill.name อยู่ใน job.title (ตรงตำแหน่ง)
    2. Soft skill → skill_type == "soft_skill"
    3. Nice-to-have → mention_count == 1 และเป็น hard_skill
    4. Hard skill → default

    mention_count: จำนวนครั้งที่ skill ถูกพูดถึงใน job description
                   (ถ้า scraper ไม่นับ ใส่ 1 ได้เลย)
    """
    skill_name_lower = skill.name.lower()
    job_title_lower  = (job.title or "").lower()

    # 1. Must-have — ชื่อ skill อยู่ใน title ตรงๆ
    if skill_name_lower in job_title_lower:
        return SCORE_MUST_HAVE

    # 2. Soft skill — สำคัญน้อยกว่า hard skill เสมอ
    if skill.skill_type == "soft_skill":
        return SCORE_SOFT_SKILL

    # 3. Nice-to-have — hard skill ที่ mention แค่ครั้งเดียว (มีแต่ไม่จำเป็น)
    if mention_count == 1 and skill.skill_type == "hard_skill":
        return SCORE_NICE_HAVE

    # 4. Hard skill ทั่วไป (mention 2+ ครั้ง = สำคัญ)
    return SCORE_HARD_SKILL


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