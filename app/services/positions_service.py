# app/services/positions_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Dict, Tuple

from app.db.models import JobPosting, JobSkill


# ---------------------------------------
# LIST POSITIONS
# ---------------------------------------
def list_positions(db: Session, limit: int = 200):

    rows = (
        db.query(
            JobPosting.sub_category_id,
            JobPosting.sub_category_name,
            func.count(JobPosting.id).label("job_count"),
        )
        .group_by(
            JobPosting.sub_category_id,
            JobPosting.sub_category_name,
        )
        .order_by(func.count(JobPosting.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(r.sub_category_id),
            "name": r.sub_category_name,
            "job_count": int(r.job_count or 0),
        }
        for r in rows
    ]


# ---------------------------------------
# GET POSITION SKILLS
# ---------------------------------------
def get_position_skills(
    db: Session,
    position_id: int,
    top_n: int = 30,
) -> Tuple[dict, List[dict]]:

    # หาตำแหน่ง
    pos = (
        db.query(
            JobPosting.sub_category_id,
            JobPosting.sub_category_name,
        )
        .filter(JobPosting.sub_category_id == position_id)
        .first()
    )

    if not pos:
        return {}, []

    # จำนวน job ทั้งหมดในตำแหน่งนี้
    total_jobs = (
        db.query(func.count(JobPosting.id))
        .filter(JobPosting.sub_category_id == position_id)
        .scalar()
        or 0
    )

    if total_jobs == 0:
        return {}, []

    # aggregate skill
    rows = (
        db.query(
            func.lower(JobSkill.skill_name).label("skill_name"),
            func.count(distinct(JobSkill.job_id)).label("cnt"),
        )
        .join(JobPosting, JobPosting.id == JobSkill.job_id)
        .filter(JobPosting.sub_category_id == position_id)
        .group_by(func.lower(JobSkill.skill_name))
        .order_by(func.count(distinct(JobSkill.job_id)).desc())
        .limit(top_n)
        .all()
    )

    skills = []

    for r in rows:
        count = int(r.cnt)
        weight = int(round((count / total_jobs) * 100))

        # demand level
        if weight >= 80:
            lvl, label = "HIGH", "ต้องการมาก"
        elif weight >= 50:
            lvl, label = "MEDIUM", "ต้องการพอสมควร"
        else:
            lvl, label = "LOW", "ต้องการน้อย"

        skills.append(
            {
                "skill_name": r.skill_name,
                "count": count,
                "weight": weight,
                "demand_level": lvl,
                "demand_label": label,
            }
        )

    pos_info = {
        "position_id": str(pos.sub_category_id),
        "position_name": pos.sub_category_name,
        "total_jobs": int(total_jobs),
    }

    return pos_info, skills


# ---------------------------------------
# MATCH % + GAP
# ---------------------------------------
def compute_match_and_gap(
    position_skills: List[dict],
    user_skills: List[dict],
):

    # normalize user score (0-5 -> 0-100)
    user_map: Dict[str, int] = {}
    for s in user_skills:
        name = (s.get("skill_name") or "").strip()
        if not name:
            continue

        score = int(s.get("score", 0))
        user_map[name.lower()] = max(0, min(score, 5)) * 20

    job_map: Dict[str, int] = {
        (x["skill_name"] or "").strip().lower(): int(x["weight"])
        for x in position_skills
    }

    labels = sorted(set(user_map.keys()) | set(job_map.keys()))

    user_data = [user_map.get(k, 0) for k in labels]
    job_data = [job_map.get(k, 0) for k in labels]

    # match %
    ratios = []
    for j, u in zip(job_data, user_data):
        if j <= 0:
            continue
        ratios.append(min(u, j) / j)

    match_percent = 0 if not ratios else round((sum(ratios) / len(ratios)) * 100)

    # gaps
    gaps = []
    for k, j, u in zip(labels, job_data, user_data):
        gap = max(j - u, 0)
        if gap > 0:
            gaps.append({"skill_name": k, "gap": int(gap)})

    gaps.sort(key=lambda x: x["gap"], reverse=True)
    gaps = gaps[:10]

    # pretty label
    pretty_labels = [
        k if any(ch.isupper() for ch in k) else k.title()
        for k in labels
    ]

    return {
        "labels": pretty_labels,
        "user_data": user_data,
        "job_data": job_data,
        "match_percent": int(match_percent),
        "gaps": gaps,
    }