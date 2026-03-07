# app/services/recommendation_engine.py


from sqlalchemy.orm import Session

from app.model.job import Job, JobSkill
from app.model.recommendation import Recommendation, RecommendationSkill
from app.model.skill import UserSkill
class RecommendationEngine:

    def generate_for_user(self, db: Session, user_id: int):

        # 🔥 1. ลบ recommendation เก่า
        db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).delete()
        db.commit()

        user_skills = db.query(UserSkill).filter(
            UserSkill.user_id == user_id
        ).all()

        user_skill_ids = {us.skill_id for us in user_skills}

        jobs = db.query(Job).all()

        recommendations = []

        for job in jobs:

            job_skills = db.query(JobSkill).filter(
                JobSkill.job_id == job.id
            ).all()

            job_skill_ids = {js.skill_id for js in job_skills}

            # 🔥 2. Skip job ถ้าไม่มี overlap
            if not user_skill_ids.intersection(job_skill_ids):
                continue

            total_score = 0
            max_score = 0

            rec = Recommendation(
                user_id=user_id,
                job_id=job.id
            )

            db.add(rec)
            db.flush()

            for js in job_skills:

                max_score += js.importance_score

                if js.skill_id in user_skill_ids:

                    matched_user_skill = next(
                        us for us in user_skills if us.skill_id == js.skill_id
                    )

                    total_score += (
                        matched_user_skill.confidence_score
                        * js.importance_score
                    )

                    match_type = "matched"

                else:
                    match_type = "missing"

                rec_skill = RecommendationSkill(
                    recommendation_id=rec.id,
                    skill_id=js.skill_id,
                    match_type=match_type
                )

                db.add(rec_skill)

            match_percent = (
                total_score / max_score * 100
                if max_score > 0 else 0
            )

            rec.match_score = total_score
            rec.skill_match_percent = match_percent

            recommendations.append(rec)

        db.commit()

        return recommendations
# class RecommendationEngine:

#     def generate_for_user(
#         self,
#         db: Session,
#         user_id: int
#     ):

#         user_skills = db.query(UserSkill).filter(
#             UserSkill.user_id == user_id
#         ).all()

#         jobs = db.query(Job).all()

#         recommendations = []

#         for job in jobs:

#             job_skills = db.query(JobSkill).filter(
#                 JobSkill.job_id == job.id
#             ).all()

#             total_score = 0
#             max_score = 0

#             for js in job_skills:
#                 max_score += js.importance_score

#                 matched = next(
#                     (us for us in user_skills if us.skill_id == js.skill_id),
#                     None
#                 )

#                 if matched:
#                     total_score += (
#                         matched.confidence_score
#                         * js.importance_score
#                     )

#             match_percent = (
#                 total_score / max_score * 100
#                 if max_score > 0 else 0
#             )

#             if total_score > 0:

#                 rec = Recommendation(
#                     user_id=user_id,
#                     job_id=job.id,
#                     match_score=total_score,
#                     skill_match_percent=match_percent
#                 )
            
#                 db.add(rec)
#                 db.flush()
#             recommendations.append(rec)
#         db.query(Recommendation).filter(
#             Recommendation.user_id == user_id
#         ).delete()
#         db.commit()

#         return recommendations
    
    