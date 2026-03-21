# app/assessment/assessment_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.job import Job, JobSkill
from app.models.skill import Skill, SkillCategory, UserSkill

from app.assessment.assessment_schema import PositionItem, PositionSkillItem, PositionSkillsResponse
from app.transcript.recommendation_engine import RecommendationEngine

MIN_JOBS     = 3
HARD_LIMIT   = 20
SOFT_LIMIT   = 12
MIN_FREQ_PCT = 5   # ต้องปรากฏใน >= 5% ของ jobs


class AssessmentService:

    def get_positions(self, db: Session) -> list[PositionItem]:
        rows = (
            db.query(SkillCategory.id, SkillCategory.name, func.count(Job.id).label("job_count"))
            .join(Job, Job.sub_category_id == SkillCategory.id)
            .group_by(SkillCategory.id, SkillCategory.name)
            .having(func.count(Job.id) >= MIN_JOBS)
            .order_by(SkillCategory.name)
            .all()
        )
        return [PositionItem(id=str(r.id), name=r.name, job_count=r.job_count) for r in rows]

    def get_position_skills(self, db: Session, sub_category_id: int) -> PositionSkillsResponse | None:
        category = db.query(SkillCategory).filter(SkillCategory.id == sub_category_id).first()
        if not category:
            return None

        total_jobs = (
            db.query(func.count(Job.id))
            .filter(Job.sub_category_id == sub_category_id)
            .scalar()
        ) or 0

        if total_jobs == 0:
            return PositionSkillsResponse(
                position_id=str(sub_category_id),
                position_name=category.name,
                total_jobs=0,
                skills=[],
            )

        job_ids_subq = db.query(Job.id).filter(Job.sub_category_id == sub_category_id)

        # ── base query: นับ distinct job ต่อ skill (= frequency จริง) ────
        base_q = (
            db.query(
                Skill.id,
                Skill.name,
                Skill.skill_type,
                func.count(func.distinct(JobSkill.job_id)).label("job_count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .filter(JobSkill.job_id.in_(job_ids_subq))
            .group_by(Skill.id, Skill.name, Skill.skill_type)
        )

        # เรียงตาม job_count desc = skill ที่ตลาดต้องการมากที่สุดก่อน
        hard_rows = (
            base_q.filter(Skill.skill_type == "hard_skill")
            .order_by(func.count(func.distinct(JobSkill.job_id)).desc())
            .limit(HARD_LIMIT)
            .all()
        )
        soft_rows = (
            base_q.filter(Skill.skill_type == "soft_skill")
            .order_by(func.count(func.distinct(JobSkill.job_id)).desc())
            .limit(SOFT_LIMIT)
            .all()
        )

        all_rows = list(hard_rows) + list(soft_rows)
        if not all_rows:
            return PositionSkillsResponse(
                position_id=str(sub_category_id),
                position_name=category.name,
                total_jobs=total_jobs,
                skills=[],
            )

        # ── weight = frequency % โดยตรง ───────────────────────────────────
        # ทั้ง hard และ soft ใช้ scale เดียวกัน (0-100 = % ของ jobs)
        # Business Analysis ที่ 73% ก็ได้ weight=73
        # Communication ที่ 73% ก็ได้ weight=73 เท่ากัน → ยุติธรรม
        skills = []
        for r in all_rows:
            freq = round(r.job_count / total_jobs * 100) if total_jobs else 0
            if freq < MIN_FREQ_PCT:
                continue
            skills.append(
                PositionSkillItem(
                    skill_id=r.id,
                    skill_name=r.name,
                    skill_type=r.skill_type,
                    weight=freq,       # weight = market demand จริง (%)
                    job_count=r.job_count,
                    frequency=freq,
                )
            )

        # เรียง hard ก่อน soft, ใน group เรียง weight desc
        skills.sort(key=lambda s: (0 if s.skill_type == "hard_skill" else 1, -s.weight))

        # ── DEBUG ──────────────────────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"[ASSESSMENT DEBUG] position='{category.name}' total_jobs={total_jobs}")
        print(f"  hard={len([s for s in skills if s.skill_type=='hard_skill'])}  "
              f"soft={len([s for s in skills if s.skill_type=='soft_skill'])}")
        for s in skills:
            print(f"  [{s.skill_type[:4]}] {s.skill_name:<30} weight={s.weight:3d}%")
        print(f"  → sent: {len(skills)} skills")
        print(f"{'='*60}\n")
        # ── END DEBUG ────────────────────────────────────────────────────

        return PositionSkillsResponse(
            position_id=str(sub_category_id),
            position_name=category.name,
            total_jobs=total_jobs,
            skills=skills,
        )

    def reset_assessment_skills(self, db: Session, user_id: int) -> int:
        deleted = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.source == "assessment")
            .delete()
        )
        db.commit()
        engine = RecommendationEngine()
        engine.generate_for_user(db, user_id)
        db.commit()
        return deleted

    def save_assessment_skills(self, db: Session, user_id: int, skill_scores: list[dict]) -> int:
        saved = 0
        for item in skill_scores:
            skill_id  = item.get("skill_id")
            raw_score = item.get("score", 0)
            if not skill_id or raw_score <= 0:
                continue

            confidence = round(raw_score / 5.0, 2)
            existing = (
                db.query(UserSkill)
                .filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
                .first()
            )
            if existing:
                if existing.source == "assessment":
                    existing.confidence_score = confidence
                    saved += 1
            else:
                db.add(UserSkill(
                    user_id=user_id,
                    skill_id=skill_id,
                    source="assessment",
                    confidence_score=confidence,
                ))
                saved += 1

        db.commit()
        if saved > 0:
            engine = RecommendationEngine()
            engine.generate_for_user(db, user_id)
            db.commit()
        return saved