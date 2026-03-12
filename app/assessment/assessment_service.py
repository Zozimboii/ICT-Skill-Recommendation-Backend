# app/services/assessment_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.job import Job, JobSkill
from app.models.skill import Skill, SkillCategory, UserSkill

from app.assessment.assessment_schema import PositionItem, PositionSkillItem, PositionSkillsResponse
from app.transcript.recommendation_engine import RecommendationEngine

MIN_JOBS = 3  # ต้องมี job ≥ 3 ถึงจะแสดง position

class AssessmentService:
        
    def get_positions(self, db: Session) -> list[PositionItem]:
        """list sub_categories ที่มี jobs พอ"""
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
        """
        คำนวณ top skills สำหรับ position
        weight = avg(importance_score) ของ skill นั้นใน jobs ของ sub_category
        normalize เป็น 0-100
        """
        category = db.query(SkillCategory).filter(SkillCategory.id == sub_category_id).first()
        if not category:
            return None

        total_jobs = (
            db.query(func.count(Job.id))
            .filter(Job.sub_category_id == sub_category_id)
            .scalar()
        ) or 0

        # avg importance_score per skill + จำนวน jobs ที่ใช้ skill นั้น
        rows = (
            db.query(
                Skill.id,
                Skill.name,
                Skill.skill_type,
                func.avg(JobSkill.importance_score).label("avg_score"),
                func.count(JobSkill.job_id).label("job_count"),
            )
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .filter(JobSkill.job_id.in_(db.query(Job.id).filter(Job.sub_category_id == sub_category_id)))
            .group_by(Skill.id, Skill.name, Skill.skill_type)
            .order_by(func.avg(JobSkill.importance_score).desc())
            .limit(20)
            .all()
        )

        if not rows:
            return PositionSkillsResponse(
                position_id=str(sub_category_id),
                position_name=category.name,
                total_jobs=total_jobs,
                skills=[],
            )

        # normalize weight เป็น 0-100
        max_score = max(r.avg_score for r in rows) or 1.0
        skills = [
            PositionSkillItem(
                skill_id=r.id,
                skill_name=r.name,
                skill_type=r.skill_type,
                weight=round((r.avg_score / max_score) * 100),
                job_count=r.job_count,
                frequency=round(r.job_count / total_jobs * 100) if total_jobs else 0,
            )
            for r in rows
        ]

        return PositionSkillsResponse(
            position_id=str(sub_category_id),
            position_name=category.name,
            total_jobs=total_jobs,
            skills=skills,
        )


    def reset_assessment_skills(self, db: Session, user_id: int) -> int:
        """ลบ assessment skills ทั้งหมด + re-generate recommendations"""

        deleted = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.source == "assessment")
            .delete()
        )
        db.commit()

        # re-generate recommendations จาก skills ที่เหลือ (transcript/ai)
        engine = RecommendationEngine()
        engine.generate_for_user(db, user_id)
        db.commit()

        return deleted


    def save_assessment_skills(
        self, 
        db: Session,
        user_id: int,
        skill_scores: list[dict],  # [{"skill_id": int, "score": float 0-5}]
    ) -> int:
        """
        บันทึก/อัปเดต user_skills จาก assessment
        score 0-5 → confidence_score 0-1
        คืนค่า จำนวน skills ที่บันทึก
        """

        saved = 0
        for item in skill_scores:
            skill_id = item.get("skill_id")
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

        # ── regenerate recommendations ────────────────────────────────────
        if saved > 0:
            engine = RecommendationEngine()
            engine.generate_for_user(db, user_id)
            db.commit()

        return saved