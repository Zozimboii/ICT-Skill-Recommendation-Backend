# backend/app/services/trends_service.py
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from app.db.models import JobPosting, JobSkill


# def get_jobsdb_trend(db: Session, days: int = 60):
#     limit_date = datetime.now().date() - timedelta(days=days)

#     results = (
#         db.query(
#             JobPosting.sub_category_id,
#             JobPosting.sub_category_name,
#             JobPosting.main_category_name,
#             func.count(JobPosting.job_id).label("job_count"),
#         )
#         .filter(JobPosting.snapshot_date >= limit_date)
#         .group_by(
#             JobPosting.sub_category_id,
#             JobPosting.sub_category_name,
#             JobPosting.main_category_name,
#         )
#         .all()
#     )

#     return {
#         "series": [
#             {
#                 "sub_category_id": r.sub_category_id,
#                 "sub_category_name": r.sub_category_name,
#                 "main_category_name": r.main_category_name,
#                 "job_count": r.job_count,
#             }
#             for r in results
#         ]
#     }


# def get_skills_trend(db: Session, days: int = 60):
#     limit_date = datetime.now().date() - timedelta(days=days)

#     results = (
#         db.query(
#             JobSkill.skill_name,
#             JobSkill.skill_type,
#             JobPosting.sub_category_id,
#             func.count(JobSkill.id).label("count"),
#         )
#         .join(JobPosting, JobSkill.job_id == JobPosting.job_id)
#         .filter(JobPosting.snapshot_date >= limit_date)
#         .group_by(
#             JobSkill.skill_name,
#             JobSkill.skill_type,
#             JobPosting.sub_category_id,
#         )
#         .all()
#     )

#     return {
#         "series": [
#             {
#                 "skill_name": r.skill_name,
#                 "skill_type": r.skill_type,
#                 "sub_category_id": r.sub_category_id,
#                 "count": r.count,
#             }
#             for r in results
#         ]
#     }
