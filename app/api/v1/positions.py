# # app/api/v1/positions.py
# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy import distinct, func, select
# from sqlalchemy.orm import Session

# from app.core.database import get_db

# from app.schemas.positions import (
#     GapItem,
#     MatchResponse,
#     PositionItem,
#     PositionSkill,
#     PositionSkillsResponse,
#     UserSkillScore,
# )
# from app.model.job import Job, JobSkill

# router = APIRouter()


# def _demand(weight: int):
#     """แปลง weight (0-100) -> ระดับความต้องการ"""
#     if weight >= 80:
#         return ("HIGH", "ต้องการมาก")
#     if weight >= 50:
#         return ("MEDIUM", "ต้องการพอสมควร")
#     return ("LOW", "ต้องการน้อย")



# def _get_position_skills(db: Session, position_id: int, limit: int = 30):

#     # total jobs ของตำแหน่งนี้
#     total_jobs = (
#         db.query(func.count(Job.id))
#         .filter(Job.sub_category_id == position_id)
#         .scalar()
#         or 0
#     )

#     if total_jobs == 0:
#         return 0, []

#     rows = (
#         db.query(
#             func.lower(JobSkill.skill_name).label("skill_name"),
#             func.count(func.distinct(JobSkill.job_id)).label("count"),
#         )
#         .join(Job, Job.id == JobSkill.job_id)
#         .filter(Job.sub_category_id == position_id)
#         .group_by(func.lower(JobSkill.skill_name))
#         .order_by(func.count(func.distinct(JobSkill.job_id)).desc())
#         .limit(limit)
#         .all()
#     )

#     skills = []

#     for skill_name, cnt in rows:
#         weight = int(round((cnt / total_jobs) * 100))

#         if weight >= 80:
#             lvl, label = "HIGH", "ต้องการมาก"
#         elif weight >= 50:
#             lvl, label = "MEDIUM", "ต้องการพอสมควร"
#         else:
#             lvl, label = "LOW", "ต้องการน้อย"

#         skills.append(
#             {
#                 "skill_name": skill_name,
#                 "count": int(cnt),
#                 "weight": weight,
#                 "demand_level": lvl,
#                 "demand_label": label,
#             }
#         )

#     return total_jobs, skills

# @router.get("", response_model=list[PositionItem])
# def list_positions(
#     db: Session = Depends(get_db),
#     limit: int = Query(100, ge=1, le=500),
# ):

#     rows = (
#         db.query(
#             Job.sub_category_id,
#             Job.sub_category_name,
#             func.count(Job.id).label("job_count"),
#         )
#         .group_by(
#             Job.sub_category_id,
#             Job.sub_category_name,
#         )
#         .order_by(func.count(Job.id).desc())
#         .limit(limit)
#         .all()
#     )

#     return [
#         PositionItem(
#             id=str(r.sub_category_id),
#             name=r.sub_category_name,
#             main_category_id=None,
#             main_category_name=None,
#             job_count=r.job_count,
#         )
#         for r in rows
#     ]

# # @router.get("/{id}/skills", response_model=PositionSkillsResponse)
# # def get_position_skills(
# #     id: int,
# #     db: Session = Depends(get_db),
# #     limit: int = Query(30, ge=1, le=200),
# # ):

# #     # หา position name จาก JobPosting
# #     pos = (
# #         db.query(
# #             JobPosting.sub_category_id,
# #             JobPosting.sub_category_name
# #         )
# #         .filter(JobPosting.sub_category_id == id)
# #         .first()
# #     )

# #     if not pos:
# #         raise HTTPException(status_code=404, detail="Position not found")

# #     total_jobs, skills = _get_position_skills(db, id, limit=limit)

# #     return PositionSkillsResponse(
# #         position_id=str(pos.sub_category_id),
# #         position_name=pos.sub_category_name,
# #         total_jobs=int(total_jobs),
# #         skills=[PositionSkill(**s) for s in skills],
# #     )

# # @router.post("/{id}/match", response_model=MatchResponse)
# # def match_position(
# #     id: int,
# #     user_skills: list[UserSkillScore],
# #     db: Session = Depends(get_db),
# #     limit: int = Query(30, ge=1, le=200),
# # ):

# #     pos = (
# #         db.query(
# #             JobPosting.sub_category_id,
# #             JobPosting.sub_category_name
# #         )
# #         .filter(JobPosting.sub_category_id == id)
# #         .first()
# #     )

# #     if not pos:
# #         raise HTTPException(status_code=404, detail="Position not found")

# #     _total_jobs, job_skills = _get_position_skills(db, id, limit=limit)

# #     # normalize user score -> 0-100
# #     user_map = {}
# #     for s in user_skills:
# #         name = s.skill_name.strip()
# #         if not name:
# #             continue
# #         user_map[name.lower()] = int(s.score) * 20

# #     job_map = {s["skill_name"].strip().lower(): int(s["weight"]) for s in job_skills}

# #     labels = list({*user_map.keys(), *job_map.keys()})
# #     labels.sort()

# #     user_data = [user_map.get(k, 0) for k in labels]
# #     job_data = [job_map.get(k, 0) for k in labels]

# #     ratios = []
# #     for j, u in zip(job_data, user_data):
# #         if j <= 0:
# #             continue
# #         ratios.append(min(u, j) / j)

# #     match_percent = int(round((sum(ratios) / len(ratios)) * 100)) if ratios else 0

# #     gaps = []
# #     for key, j, u in zip(labels, job_data, user_data):
# #         gap = max(j - u, 0)
# #         if gap > 0:
# #             gaps.append(GapItem(skill_name=key, gap=int(gap)))

# #     gaps = sorted(gaps, key=lambda x: x.gap, reverse=True)[:10]

# #     return MatchResponse(
# #         position_id=str(pos.sub_category_id),
# #         position_name=pos.sub_category_name,
# #         match_percent=match_percent,
# #         labels=labels,
# #         user_data=user_data,
# #         job_data=job_data,
# #         gaps=gaps,
# #     )