#  app/services/transcript_match/recommendation_engine.py


from sqlalchemy.orm import Session

from app.model.job import Job, JobSkill
from app.model.recommendation import Recommendation, RecommendationSkill
from app.model.skill import UserSkill


class RecommendationEngine:

    def generate_for_user(self, db: Session, user_id: int):

        # 1. ลบ recommendation เก่า
        db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).delete()
        db.flush()

        user_skills = db.query(UserSkill).filter(
            UserSkill.user_id == user_id
        ).all()

        if not user_skills:
            return []

        # user_skill lookup: skill_id → confidence_score
        user_skill_map: dict[int, float] = {
            us.skill_id: us.confidence_score for us in user_skills
        }
        user_skill_ids = set(user_skill_map.keys())

        jobs = db.query(Job).all()
        recommendations = []

        for job in jobs:
            job_skills = db.query(JobSkill).filter(
                JobSkill.job_id == job.id
            ).all()

            if not job_skills:
                continue

            job_skill_ids = {js.skill_id for js in job_skills}

            # Skip job ที่ไม่มี overlap เลย
            if not user_skill_ids.intersection(job_skill_ids):
                continue

            # ── คำนวณ score ──────────────────────────────────────────────────
            # max_score  = sum ของ importance_score ทุก skill ที่ job ต้องการ
            # total_score = sum ของ (confidence × importance) เฉพาะที่ user มี
            #
            # ผลลัพธ์: skill สำคัญ (must-have score=4) ถ้า user ไม่มี → ลด % เยอะ
            #          skill เสริม (soft score=1)       ถ้าไม่มี → ลด % นิดหน่อย

            max_score   = sum(js.importance_score for js in job_skills)
            total_score = 0.0

            rec = Recommendation(user_id=user_id, job_id=job.id)
            db.add(rec)
            db.flush()

            for js in job_skills:
                if js.skill_id in user_skill_ids:
                    confidence  = user_skill_map[js.skill_id]
                    total_score += confidence * js.importance_score
                    match_type  = "matched"
                else:
                    match_type  = "missing"

                db.add(RecommendationSkill(
                    recommendation_id=rec.id,
                    skill_id=js.skill_id,
                    match_type=match_type
                ))

            rec.match_score          = round(total_score, 4)
            rec.skill_match_percent  = round(
                total_score / max_score * 100 if max_score > 0 else 0, 2
            )
            recommendations.append(rec)

        return recommendations