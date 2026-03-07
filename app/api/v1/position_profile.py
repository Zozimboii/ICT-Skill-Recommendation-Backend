# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from typing import List


# from backend.app.db.database import get_db
# from backend.app.db.models import JobSnapshot



# router = APIRouter(prefix="/positions", tags=["Position Profile"])


# # ----------------------------
# # Response Schema
# # ----------------------------

# def classify_demand(weight: float) -> str:
#     if weight >= 70:
#         return "HIGH"
#     elif weight >= 40:
#         return "MEDIUM"
#     return "LOW"


# @router.get("/{sub_category_id}/profile")
# def get_position_profile(sub_category_id: int, db: Session = Depends(get_db)):

#     # 1️⃣ ดึง job ทั้งหมดในตำแหน่งนี้
#     job_rows = (
#         db.query(JobSnapshot.job_id)
#         .filter(JobSnapshot.sub_category_id == sub_category_id)
#         .distinct()
#         .all()
#     )

#     if not job_rows:
#         raise HTTPException(status_code=404, detail="No jobs found for this position")

#     job_ids = [row[0] for row in job_rows]
#     total_jobs = len(job_ids)

#     # 2️⃣ ดึง skill frequency
#     skill_rows = (
#         db.query(
#             JobSkills.skill_name,
#             func.count(JobSkills.skill_name).label("count"),
#         )
#         .filter(JobSkills.job_id.in_(job_ids))
#         .group_by(JobSkills.skill_name)
#         .all()
#     )

#     skills = []

#     for skill_name, count in skill_rows:
#         weight = round((count / total_jobs) * 100, 2)

#         skills.append(
#             {
#                 "skill_name": skill_name,
#                 "weight": weight,
#                 "demand_level": classify_demand(weight),
#             }
#         )

#     # sort จากมากไปน้อย
#     skills.sort(key=lambda x: x["weight"], reverse=True)

#     # ดึงชื่อ position
#     position_name_row = (
#         db.query(JobSnapshot.sub_category_name)
#         .filter(JobSnapshot.sub_category_id == sub_category_id)
#         .first()
#     )

#     position_name = position_name_row[0] if position_name_row else "Unknown"

#     return {
#         "position_id": sub_category_id,
#         "position_name": position_name,
#         "total_jobs": total_jobs,
#         "skills": skills[:50],  # limit top 50
#     }