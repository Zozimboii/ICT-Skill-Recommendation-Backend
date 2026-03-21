# app/services/dashboard_service.py
from sqlalchemy.orm import Session

from app.utils.skill_groups import group_skills
from app.utils.career_path import build_career_path
from app.dashboard.dashboard_schema import (
    CareerPathStep, DashboardSummary, RecommendationItem,
    SkillGapItem, SkillGapResponse, SkillGroupItem,
)
from app.models.job import Job, JobSkill
from app.models.recommendation import Recommendation, RecommendationSkill
from app.models.skill import Skill, UserSkill
from app.models.transcript import Transcript

# ── Thresholds ────────────────────────────────────────────────────────────────
FREQUENCY_THRESHOLD = 0.10   # < 10%  = noise ตัดทิ้ง
FREQ_REQUIRED       = 0.50   # >= 50% = required
FREQ_RECOMMENDED    = 0.20   # >= 20% = recommended
MAX_SKILL_GAP_RECS  = 5
MAX_RECOMMENDATIONS = 5

# ── Helper functions (module-level ไม่ใช่ method) ─────────────────────────────

def _importance_tier_by_freq(freq: float | None) -> str:
    """ตัดสิน importance จาก market demand จริง (frequency %)"""
    f = freq or 0.0
    if f >= FREQ_REQUIRED:      return "required"
    if f >= FREQ_RECOMMENDED:   return "recommended"
    return "optional"


def _is_meaningful(importance: str, freq: float | None) -> bool:
    """นับใน match score ไหม"""
    if importance == "required":
        return True
    if importance == "recommended":
        return (freq or 0) >= FREQUENCY_THRESHOLD
    return False


def _should_include(freq: float | None) -> bool:
    """แสดงใน missing list ไหม"""
    return (freq or 0) >= FREQUENCY_THRESHOLD


# ── Service class ─────────────────────────────────────────────────────────────

class DashboardService:

    def get_summary(self, db: Session, user_id: int) -> DashboardSummary:
        transcript = db.query(Transcript).filter(Transcript.user_id == user_id).first()

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
            has_transcript=True,
        )

    def _get_rec_skills(self, db: Session, rec: Recommendation):
        """ดึง skills พร้อม importance_score สำหรับ recommendation นี้"""
        return (
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

    def get_skill_gap(self, db: Session, user_id: int) -> list[SkillGapResponse]:
        recommendations = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.match_score.desc())
            .limit(MAX_SKILL_GAP_RECS)
            .all()
        )

        result = []
        for rec in recommendations:
            job = db.query(Job).filter(Job.id == rec.job_id).first()
            if not job:
                continue

            rec_skills = self._get_rec_skills(db, rec)

            # ── matched ───────────────────────────────────────────────────────
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
                    importance=_importance_tier_by_freq(skill.frequency_score),
                    frequency_score=skill.frequency_score,
                )
                for skill, imp in matched_all
            ]
            matched_meaningful_count = sum(
                1 for skill, imp in matched_all
                if _is_meaningful(
                    _importance_tier_by_freq(skill.frequency_score),
                    skill.frequency_score,
                )
            )

            # ── missing ───────────────────────────────────────────────────────
            missing_raw = [
                (skill, imp or 0.5)
                for rs, skill, imp in rec_skills
                if rs.match_type == "missing"
            ]
            missing_filtered = [
                (skill, imp)
                for skill, imp in missing_raw
                if _should_include(skill.frequency_score)
            ]
            missing_meaningful_count = sum(
                1 for skill, imp in missing_filtered
                if _is_meaningful(
                    _importance_tier_by_freq(skill.frequency_score),
                    skill.frequency_score,
                )
            )

            meaningful_total = matched_meaningful_count + missing_meaningful_count
            skill_match_pct = (
                (matched_meaningful_count / meaningful_total * 100)
                if meaningful_total > 0
                else float(rec.skill_match_percent)
            )

            # เรียง: required ก่อน → recommended → optional, แล้ว freq desc
            missing_sorted = sorted(
                missing_filtered,
                key=lambda x: (
                    0 if _importance_tier_by_freq(x[0].frequency_score) == "required" else
                    1 if _importance_tier_by_freq(x[0].frequency_score) == "recommended" else 2,
                    -(x[0].frequency_score or 0),
                ),
            )

            top10 = [
                SkillGapItem(
                    skill_name=skill.name,
                    skill_type=skill.skill_type,
                    status="missing",
                    importance=_importance_tier_by_freq(skill.frequency_score),
                    frequency_score=skill.frequency_score,
                )
                for skill, imp in missing_sorted[:10]
            ]

            all_missing_dicts = [
                {
                    "skill_name":      skill.name,
                    "skill_type":      skill.skill_type,
                    "status":          "missing",
                    "importance":      _importance_tier_by_freq(skill.frequency_score),
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

            career_path = [
                CareerPathStep(**step)
                for step in build_career_path(all_missing_dicts, max_steps=5)
            ]

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
                    total_job_skills=meaningful_total,
                    matched_count=matched_meaningful_count,
                    missing_group_count=len(missing_by_group),
                )
            )

        return result

    def get_recommendations(self, db: Session, user_id: int) -> list[RecommendationItem]:
        recs = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.match_score.desc())
            .limit(MAX_RECOMMENDATIONS)
            .all()
        )

        result = []
        for rec in recs:
            job = db.query(Job).filter(Job.id == rec.job_id).first()
            if not job:
                continue

            rec_skills = self._get_rec_skills(db, rec)

            matched_meaningful = sum(
                1 for rs, skill, imp in rec_skills
                if rs.match_type == "matched"
                and _is_meaningful(
                    _importance_tier_by_freq(skill.frequency_score),
                    skill.frequency_score,
                )
            )
            missing_meaningful = sum(
                1 for rs, skill, imp in rec_skills
                if rs.match_type == "missing"
                and _is_meaningful(
                    _importance_tier_by_freq(skill.frequency_score),
                    skill.frequency_score,
                )
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