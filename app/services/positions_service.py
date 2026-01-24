# app/services/positions_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, select
from typing import List, Dict, Tuple

from app.db.models import JobCountBySubCategory, JobSkillsWithCategories, JobsSkill

def list_positions(db: Session, limit: int = 200, main_category_id: str | None = None):
    q = db.query(JobCountBySubCategory)

    if main_category_id:
        q = q.filter(JobCountBySubCategory.main_category_id == main_category_id)

    rows = (
        q.order_by(JobCountBySubCategory.job_count.desc())
         .limit(limit)
         .all()
    )

    return [
        {
            "id": str(r.sub_category_id),
            "name": r.sub_category_name,
            "job_count": int(r.job_count or 0),
            "main_category_id": getattr(r, "main_category_id", None),
            "main_category_name": getattr(r, "main_category_name", None),
        }
        for r in rows
    ]

def _get_position_row(db: Session, position_id: str):
    return (
        db.query(JobCountBySubCategory)
          .filter(JobCountBySubCategory.sub_category_id == position_id)
          .first()
    )

def _job_ids_for_position_subcat(db: Session, position_id: str):
    # job_id ทั้งหมดที่อยู่ใน sub_category นี้
    # ใช้ distinct กันซ้ำ
    return (
        db.query(distinct(JobSkillsWithCategories.job_id).label("job_id"))
          .filter(JobSkillsWithCategories.sub_category_id == position_id)
          .subquery()
    )

def get_position_skills(db: Session, position_id: str, top_n: int = 25) -> Tuple[dict, List[dict]]:
    pos = _get_position_row(db, position_id)
    if not pos:
        return {}, []

    job_ids_subq = _job_ids_for_position_subcat(db, position_id)

    # count skill จาก JobsSkill โดยดูเฉพาะ job_id ที่อยู่ในตำแหน่งนี้
    rows = (
        db.query(
            JobsSkill.skill_name.label("skill_name"),
            func.count(distinct(JobsSkill.job_id)).label("cnt"),
        )
        .filter(JobsSkill.job_id.in_(select(job_ids_subq.c.job_id)))
        .group_by(JobsSkill.skill_name)
        .order_by(func.count(distinct(JobsSkill.job_id)).desc())
        .limit(top_n)
        .all()
    )

    # แปลงเป็น weight 0-100 (normalize โดยเทียบกับตัวบนสุด)
    max_cnt = int(rows[0].cnt) if rows else 0
    skills = []
    for r in rows:
        c = int(r.cnt)
        weight = 0 if max_cnt == 0 else round((c / max_cnt) * 100)
        skills.append({"skill_name": r.skill_name, "count": c, "weight": int(weight)})

    pos_info = {
        "position_id": str(pos.sub_category_id),
        "position_name": pos.sub_category_name,
        "total_jobs": int(pos.job_count or 0),
    }
    return pos_info, skills

# ---------- Match % + Gap ----------
def compute_match_and_gap(
    position_skills: List[dict],
    user_skills: List[dict],  # [{skill_name, score}]
):
    # normalize user score (0-5) -> 0-100
    user_map: Dict[str, int] = {}
    for s in user_skills:
        name = (s["skill_name"] or "").strip()
        if not name:
            continue
        score = int(s.get("score", 0))
        user_map[name.lower()] = max(0, min(score, 5)) * 20

    job_map: Dict[str, int] = { (x["skill_name"] or "").strip().lower(): int(x["weight"]) for x in position_skills }

    labels = sorted(set(list(user_map.keys()) + list(job_map.keys())))

    user_data = [user_map.get(k, 0) for k in labels]
    job_data  = [job_map.get(k, 0) for k in labels]

    # match percent = เฉลี่ย(min(user, job)/job) เฉพาะที่ job>0
    ratios = []
    for j, u in zip(job_data, user_data):
        if j <= 0:
            continue
        ratios.append(min(u, j) / j)

    match_percent = 0 if not ratios else round((sum(ratios) / len(ratios)) * 100)

    # gaps = job - user (เฉพาะที่ job>user)
    gaps = []
    for k, j, u in zip(labels, job_data, user_data):
        gap = max(j - u, 0)
        if gap > 0:
            gaps.append({"skill_name": k, "gap": int(gap)})

    gaps.sort(key=lambda x: x["gap"], reverse=True)
    gaps = gaps[:10]

    # แปลง label กลับเป็นชื่อเดิมแบบอ่านง่าย (capitalize)
    pretty_labels = [k if any(ch.isupper() for ch in k) else k.title() for k in labels]

    return {
        "labels": pretty_labels,
        "user_data": user_data,
        "job_data": job_data,
        "match_percent": int(match_percent),
        "gaps": gaps,
    }


