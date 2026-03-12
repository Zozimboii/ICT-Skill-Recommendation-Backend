# app/services/dashboard_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transcript import Transcript
from app.models.skill import Skill, UserSkill
from app.models.recommendation import Recommendation, RecommendationSkill
from app.models.job import Job, JobSkill
from app.dashboard.dashboard_schema import (
    DashboardSummary,
    SkillGapItem,
    SkillGapResponse,
    SkillGroupItem,
    CareerPathStep,
    RecommendationItem,
)
from app.utils.skill_groups import group_skills
from app.utils.career_path import build_career_path
from app.utils.skill_importance import importance_tier, is_meaningful, should_include

class DashboardService:

    def get_summary(self, db: Session, user_id: int) -> DashboardSummary:
        transcript = db.query(Transcript).filter(Transcript.user_id == user_id).first()

        # มี skills จาก assessment ก็ถือว่าใช้ dashboard ได้
        has_assessment_skills = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.source == "assessment")
            .first()
        ) is not None

        if not transcript and not has_assessment_skills:
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
        rec_count = db.query(Recommendation).filter(Recommendation.user_id == user_id).count()

        return DashboardSummary(
            gpa=float(transcript.gpa) if transcript and transcript.gpa else None,
            university=transcript.university if transcript else None,
            major=transcript.major if transcript else None,
            hard_skill_count=hard_count,
            soft_skill_count=soft_count,
            recommendation_count=rec_count,
            has_transcript=True,   # ← True ถ้ามี transcript หรือ assessment skills
        )

    def get_skill_gap(self, db: Session, user_id: int) -> list[SkillGapResponse]:
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

            rec_skills = (
                db.query(RecommendationSkill, Skill, JobSkill.importance_score)
                .join(Skill, RecommendationSkill.skill_id == Skill.id)
                .outerjoin(
                    JobSkill,
                    (JobSkill.job_id == rec.job_id) &
                    (JobSkill.skill_id == RecommendationSkill.skill_id),
                )
                .filter(RecommendationSkill.recommendation_id == rec.id)
                .all()
            )

            # ── matched ───────────────────────────────────────────────────
            matched_all = [
                (skill, imp or 0.5)
                for rs, skill, imp in rec_skills
                if rs.match_type == "matched"
            ]

            matched_items = [
                SkillGapItem(
                    skill_name=skill.name,
                    skill_type=skill.skill_type,
                    status="matched",
                    importance=importance_tier(imp),
                    frequency_score=skill.frequency_score,
                )
                for skill, imp in matched_all
            ]

            # นับเฉพาะ meaningful สำหรับ display number
            matched_meaningful_count = sum(
                1 for skill, imp in matched_all
                if is_meaningful(importance_tier(imp), skill.frequency_score)
            )

            # ── missing ───────────────────────────────────────────────────
            missing_raw = [
                (skill, imp or 0.5)
                for rs, skill, imp in rec_skills
                if rs.match_type == "missing"
            ]

            missing_filtered = [
                (skill, imp) for skill, imp in missing_raw
                if should_include(skill.frequency_score, importance_tier(imp))
            ]

            # นับ meaningful missing สำหรับ denominator
            missing_meaningful_count = sum(
                1 for skill, imp in missing_filtered
                if is_meaningful(importance_tier(imp), skill.frequency_score)
            )

            # denominator = meaningful matched + meaningful missing
            meaningful_total = matched_meaningful_count + missing_meaningful_count

            skill_match_pct = (
                (matched_meaningful_count / meaningful_total * 100)
                if meaningful_total > 0
                else float(rec.skill_match_percent)
            )

            missing_sorted = sorted(
                missing_filtered,
                key=lambda x: (
                    0 if importance_tier(x[1]) == "required" else
                    1 if importance_tier(x[1]) == "recommended" else 2,
                    -(x[0].frequency_score or 0),
                ),
            )

            top10 = [
                SkillGapItem(
                    skill_name=skill.name,
                    skill_type=skill.skill_type,
                    status="missing",
                    importance=importance_tier(imp),
                    frequency_score=skill.frequency_score,
                )
                for skill, imp in missing_sorted[:10]
            ]

            all_missing_dicts = [
                {
                    "skill_name": skill.name,
                    "skill_type": skill.skill_type,
                    "status": "missing",
                    "importance": importance_tier(imp),
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

            career_path_raw = build_career_path(all_missing_dicts, max_steps=5)
            career_path = [CareerPathStep(**step) for step in career_path_raw]

            result.append(
                SkillGapResponse(
                    job_title=job.title,
                    company_name=job.company_name,
                    sub_category=job.sub_category.name if job.sub_category else None,
                    match_score=float(rec.match_score),
                    skill_match_percent=skill_match_pct,
                    matched_skills=matched_items,
                    missing_skills=top10,
                    missing_by_group=missing_by_group,
                    career_path=career_path,
                    total_missing=len(missing_sorted),
                    total_job_skills=meaningful_total,        # ← required+recommended only
                    matched_count=matched_meaningful_count,   # ← required+recommended only
                    missing_group_count=len(missing_by_group),
                )
            )

        return result


    def get_recommendations(self, db: Session, user_id: int) -> list[RecommendationItem]:
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

            rec_skills = (
                db.query(RecommendationSkill, Skill, JobSkill.importance_score)
                .join(Skill, RecommendationSkill.skill_id == Skill.id)
                .outerjoin(
                    JobSkill,
                    (JobSkill.job_id == rec.job_id) &
                    (JobSkill.skill_id == RecommendationSkill.skill_id),
                )
                .filter(RecommendationSkill.recommendation_id == rec.id)
                .all()
            )

            matched_meaningful = sum(
                1 for rs, skill, imp in rec_skills
                if rs.match_type == "matched"
                and is_meaningful(importance_tier(imp or 0.5), skill.frequency_score)
            )
            missing_meaningful = sum(
                1 for rs, skill, imp in rec_skills
                if rs.match_type == "missing"
                and is_meaningful(importance_tier(imp or 0.5), skill.frequency_score)
            )
            total_meaningful = matched_meaningful + missing_meaningful

            skill_match_pct = (
                (matched_meaningful / total_meaningful * 100)
                if total_meaningful > 0
                else float(rec.skill_match_percent)
            )

            result.append(
                RecommendationItem(
                    id=rec.id,
                    job_id=rec.job_id,
                    title=job.title,
                    company_name=job.company_name,
                    location=job.location,
                    sub_category=job.sub_category.name if job.sub_category else None,
                    match_score=float(rec.match_score),
                    skill_match_percent=skill_match_pct,
                    matched_count=matched_meaningful,
                    total_skill_count=total_meaningful,
                )
            )

        return result