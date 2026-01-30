# app/api/v1/positions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import JobCountBySubCategory, JobSkillsWithCategories, JobsSkill
from app.schemas.positions import (
    GapItem,
    MatchResponse,
    PositionItem,
    PositionSkill,
    PositionSkillsResponse,
    UserSkillScore,
)

router = APIRouter()


def _demand(weight: int):
    """แปลง weight (0-100) -> ระดับความต้องการ"""
    if weight >= 80:
        return ("HIGH", "ต้องการมาก")
    if weight >= 50:
        return ("MEDIUM", "ต้องการพอสมควร")
    return ("LOW", "ต้องการน้อย")


def _load_position_row(db: Session, position_id: int):
    row = (
        db.query(JobCountBySubCategory)
        .filter(JobCountBySubCategory.sub_category_id == position_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Position not found")
    return row


def _get_position_skills(db: Session, position_id: int, limit: int = 30):
    """
    aggregate skill จาก JobsSkill โดยอิง job_id ที่อยู่ใน sub_category_id นั้น
    และคำนวณ weight 0-100 + demand_level/demand_label
    """
    # job_ids ของตำแหน่งนั้น (จาก job_skills_with_categories)
    job_ids_subq = (
        db.query(JobSkillsWithCategories.job_id)
        .filter(JobSkillsWithCategories.sub_category_id == position_id)
        .subquery()
    )

    total_jobs = (
        db.query(func.count(distinct(JobSkillsWithCategories.job_id)))
        .filter(JobSkillsWithCategories.sub_category_id == position_id)
        .scalar()
        or 0
    )

    if total_jobs == 0:
        return total_jobs, []

    # นับ skill ต่อจำนวน job ที่พบ skill นั้น
    rows = (
        db.query(
            JobsSkill.skill_name.label("skill_name"),
            func.count(distinct(JobsSkill.job_id)).label("count"),
        )
        .filter(JobsSkill.job_id.in_(select(job_ids_subq.c.job_id)))
        .group_by(JobsSkill.skill_name)
        .order_by(func.count(distinct(JobsSkill.job_id)).desc())
        .limit(limit)
        .all()
    )

    skills = []
    for skill_name, cnt in rows:
        # weight 0-100 = สัดส่วน job ในตำแหน่งนี้ที่ประกาศ skill นั้น
        weight = int(round((int(cnt) / int(total_jobs)) * 100))
        lvl, label = _demand(weight)

        skills.append(
            {
                "skill_name": skill_name,
                "count": int(cnt),
                "weight": weight,
                "demand_level": lvl,
                "demand_label": label,
            }
        )

    return total_jobs, skills


@router.get("", response_model=list[PositionItem])
def list_positions(
    db: Session = Depends(get_db),
    main_category_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    q = db.query(JobCountBySubCategory)
    if main_category_id is not None:
        q = q.filter(JobCountBySubCategory.main_category_id == main_category_id)

    rows = q.order_by(JobCountBySubCategory.job_count.desc()).limit(limit).all()

    return [
        PositionItem(
            id=str(r.sub_category_id),
            name=r.sub_category_name,
            main_category_id=r.main_category_id,
            main_category_name=r.main_category_name,
            job_count=r.job_count or 0,
        )
        for r in rows
    ]


@router.get("/{id}/skills", response_model=PositionSkillsResponse)
def get_position_skills(
    id: int,
    db: Session = Depends(get_db),
    limit: int = Query(30, ge=1, le=200),
):
    pos = _load_position_row(db, id)
    total_jobs, skills = _get_position_skills(db, id, limit=limit)

    return PositionSkillsResponse(
        position_id=str(pos.sub_category_id),
        position_name=pos.sub_category_name,
        total_jobs=int(total_jobs),
        skills=[PositionSkill(**s) for s in skills],
    )


@router.post("/{id}/match", response_model=MatchResponse)
def match_position(
    id: int,
    user_skills: list[UserSkillScore],
    db: Session = Depends(get_db),
    limit: int = Query(30, ge=1, le=200),
):
    pos = _load_position_row(db, id)
    _total_jobs, job_skills = _get_position_skills(db, id, limit=limit)

    # normalize user score -> 0-100
    user_map = {}
    for s in user_skills:
        name = s.skill_name.strip()
        if not name:
            continue
        user_map[name.lower()] = int(s.score) * 20  # 0-100

    job_map = {s["skill_name"].strip().lower(): int(s["weight"]) for s in job_skills}

    # รวม label
    labels = list({*user_map.keys(), *job_map.keys()})
    labels.sort()

    user_data = [user_map.get(k, 0) for k in labels]
    job_data = [job_map.get(k, 0) for k in labels]

    # match%: เฉลี่ย min(user, job)/job ของเฉพาะ skill ที่ job>0
    ratios = []
    for j, u in zip(job_data, user_data):
        if j <= 0:
            continue
        ratios.append(min(u, j) / j)

    match_percent = int(round((sum(ratios) / len(ratios)) * 100)) if ratios else 0

    # gaps: job - user (เฉพาะ gap>0)
    gaps = []
    for key, j, u in zip(labels, job_data, user_data):
        gap = max(j - u, 0)
        if gap > 0:
            gaps.append(GapItem(skill_name=key, gap=int(gap)))

    gaps = sorted(gaps, key=lambda x: x.gap, reverse=True)[:10]

    return MatchResponse(
        position_id=str(pos.sub_category_id),
        position_name=pos.sub_category_name,
        match_percent=match_percent,
        labels=labels,
        user_data=user_data,
        job_data=job_data,
        gaps=gaps,
    )
