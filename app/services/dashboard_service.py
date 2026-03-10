# app/services/dashboard_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.model.transcript import Transcript
from app.model.skill import Skill, UserSkill
from app.model.recommendation import Recommendation, RecommendationSkill
from app.model.job import Job, JobSkill
from app.schemas.dashboard import (
    DashboardSummary,
    SkillGapItem,
    SkillGapResponse,
    SkillGroupItem,
    CareerPathStep,
    RecommendationItem,
)
from app.utils.skill_groups import group_skills
from app.utils.career_path import build_career_path

FREQUENCY_THRESHOLD = 0.05  # ข้อ 9: ตัด skill ที่ปรากฏน้อยกว่า 5% ออก


def get_summary(db: Session, user_id: int) -> DashboardSummary:
    transcript = db.query(Transcript).filter(Transcript.user_id == user_id).first()
    if not transcript:
        return DashboardSummary(has_transcript=False)

    hard_count = (
        db.query(UserSkill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .filter(UserSkill.user_id == user_id, Skill.skill_type == "hard_skill")
        .count()
    )
    soft_count = (
        db.query(UserSkill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .filter(UserSkill.user_id == user_id, Skill.skill_type == "soft_skill")
        .count()
    )
    rec_count = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .count()
    )
    return DashboardSummary(
        gpa=float(transcript.gpa) if transcript.gpa else None,
        university=transcript.university,
        major=transcript.major,
        hard_skill_count=hard_count,
        soft_skill_count=soft_count,
        recommendation_count=rec_count,
        has_transcript=True,
    )


def _importance_tier(score: float) -> str:
    if score >= 2.0:
        return "required"
    elif score >= 1.0:
        return "recommended"
    return "optional"


def _should_include(freq: float | None, importance: str) -> bool:
    """
    ข้อ 9: กรอง noise skills ออก
    - required/recommended: เก็บไว้เสมอ
    - optional + freq < 5%: ตัดออก
    """
    if importance in ("required", "recommended"):
        return True
    return (freq or 0) >= FREQUENCY_THRESHOLD


def get_skill_gap(db: Session, user_id: int) -> list[SkillGapResponse]:
    recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.match_score.desc())
        .limit(3)
        .all()
    )

    result = []
    for rec in recommendations:
        job = db.query(Job).filter(Job.id == rec.job_id).first()
        if not job:
            continue

        # JOIN importance_score + frequency_score
        rec_skills = (
            db.query(
                RecommendationSkill,
                Skill,
                JobSkill.importance_score,
            )
            .join(Skill, RecommendationSkill.skill_id == Skill.id)
            .outerjoin(
                JobSkill,
                (JobSkill.job_id == rec.job_id) &
                (JobSkill.skill_id == RecommendationSkill.skill_id),
            )
            .filter(RecommendationSkill.recommendation_id == rec.id)
            .all()
        )

        # ── matched ───────────────────────────────────────────
        matched = [
            SkillGapItem(
                skill_name=skill.name,
                skill_type=skill.skill_type,
                status="matched",
                importance=_importance_tier(imp or 0.5),
                frequency_score=skill.frequency_score,
            )
            for rs, skill, imp in rec_skills
            if rs.match_type == "matched"
        ]

        # ── missing: filter noise → sort by importance desc ──
        missing_all_raw = [
            (skill, imp or 0.5)
            for rs, skill, imp in rec_skills
            if rs.match_type == "missing"
        ]

        # ข้อ 9: กรอง optional + low frequency ออก
        missing_filtered = [
            (skill, imp)
            for skill, imp in missing_all_raw
            if _should_include(skill.frequency_score, _importance_tier(imp))
        ]

        missing_sorted = sorted(
            missing_filtered,
            key=lambda x: (
                0 if _importance_tier(x[1]) == "required" else
                1 if _importance_tier(x[1]) == "recommended" else 2,
                -(x[0].frequency_score or 0),
            ),
        )

        total_missing = len(missing_sorted)

        # Phase 1: top 10 flat
        top10 = [
            SkillGapItem(
                skill_name=skill.name,
                skill_type=skill.skill_type,
                status="missing",
                importance=_importance_tier(imp),
                frequency_score=skill.frequency_score,
            )
            for skill, imp in missing_sorted[:10]
        ]

        # Phase 2: group all filtered missing
        all_missing_dicts = [
            {
                "skill_name": skill.name,
                "skill_type": skill.skill_type,
                "status": "missing",
                "importance": _importance_tier(imp),
                "frequency_score": skill.frequency_score,
            }
            for skill, imp in missing_sorted
        ]
        grouped = group_skills(all_missing_dicts)
        missing_by_group = [
            SkillGroupItem(
                group_name=gname,
                skills=[SkillGapItem(**s) for s in skills],
                count=len(skills),
            )
            for gname, skills in grouped.items()
        ]

        # Phase 3: career path
        career_path_raw = build_career_path(all_missing_dicts, max_steps=5)
        career_path = [CareerPathStep(**step) for step in career_path_raw]

        result.append(
            SkillGapResponse(
                job_title=job.title,
                company_name=job.company_name,
                sub_category=job.sub_category.name if job.sub_category else None,
                match_score=float(rec.match_score),
                skill_match_percent=float(rec.skill_match_percent),
                matched_skills=matched,
                missing_skills=top10,
                missing_by_group=missing_by_group,
                career_path=career_path,
                total_missing=total_missing,
                total_job_skills=len(matched) + len(missing_all_raw),
                matched_count=len(matched),
                missing_group_count=len(missing_by_group),
            )
        )

    return result


def get_recommendations(db: Session, user_id: int) -> list[RecommendationItem]:
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.match_score.desc())
        .limit(5)
        .all()
    )

    result = []
    for rec in recs:
        job = db.query(Job).filter(Job.id == rec.job_id).first()
        if not job:
            continue

        skill_counts = (
            db.query(
                RecommendationSkill.match_type,
                func.count(RecommendationSkill.skill_id),
            )
            .filter(RecommendationSkill.recommendation_id == rec.id)
            .group_by(RecommendationSkill.match_type)
            .all()
        )
        count_map = {mt: cnt for mt, cnt in skill_counts}
        matched_count = count_map.get("matched", 0)
        total_count = matched_count + count_map.get("missing", 0)

        result.append(
            RecommendationItem(
                id=rec.id,
                job_id=rec.job_id,
                title=job.title,
                company_name=job.company_name,
                location=job.location,
                sub_category=job.sub_category.name if job.sub_category else None,
                match_score=float(rec.match_score),
                skill_match_percent=float(rec.skill_match_percent),
                matched_count=matched_count,
                total_skill_count=total_count,
            )
        )

    return result