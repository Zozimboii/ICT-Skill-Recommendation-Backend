# scripts/cleanup_skills.py
"""
Phase: Skill Cleanup
รัน: python -m scripts.cleanup_skills

สิ่งที่ทำ:
1. Block skills ที่อยู่ใน SKILL_BLOCKLIST
2. Merge alias skills → canonical skill
3. ลบ canonical ซ้ำ
4. รายงานผล

รันหลัง: python -m scripts.seed_skill_aliases
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.skill import Skill, SkillAlias, UserSkill
from app.models.job import JobSkill

from app.models.recommendation import RecommendationSkill
from app.utils.canonical_skills import SKILL_BLOCKLIST, SKILL_ALIASES, CANONICAL_SKILLS
from sqlalchemy.orm import Session


def cleanup_skills():
    db = SessionLocal()
    try:
        all_skills = db.query(Skill).all()
        print(f"Total skills before cleanup: {len(all_skills)}")

        blocked = 0
        merged = 0
        kept = 0

        for skill in all_skills:
            name_lower = skill.name.strip().lower()

            # ── 1. Block ────────────────────────────────────────
            if name_lower in {b.lower() for b in SKILL_BLOCKLIST}:
                _delete_skill(db, skill)
                blocked += 1
                continue

            # ── 2. Alias → Canonical ────────────────────────────
            canonical_name = SKILL_ALIASES.get(name_lower)
            if canonical_name:
                canonical_skill = db.query(Skill).filter(
                    Skill.name == canonical_name
                ).first()

                if not canonical_skill:
                    # สร้าง canonical skill ถ้ายังไม่มี
                    skill_type = CANONICAL_SKILLS.get(canonical_name, skill.skill_type)
                    canonical_skill = Skill(name=canonical_name, skill_type=skill_type)
                    db.add(canonical_skill)
                    db.flush()

                if canonical_skill.id != skill.id:
                    # ย้าย references ทั้งหมดไปที่ canonical
                    _reassign_skill_references(db, old_id=skill.id, new_id=canonical_skill.id)
                    _delete_skill(db, skill)
                    merged += 1
                    print(f"  MERGE: '{skill.name}' → '{canonical_name}'")
                continue

            # ── 3. Fix casing ────────────────────────────────────
            canonical_lower = {k.lower(): k for k in CANONICAL_SKILLS}
            if name_lower in canonical_lower:
                correct_name = canonical_lower[name_lower]
                if skill.name != correct_name:
                    print(f"  FIX CASE: '{skill.name}' → '{correct_name}'")
                    skill.name = correct_name

            kept += 1

        db.commit()

        after_count = db.query(Skill).count()
        print(f"\n{'='*50}")
        print(f"Cleanup complete:")
        print(f"  Blocked (deleted):  {blocked}")
        print(f"  Merged (aliases):   {merged}")
        print(f"  Kept:               {kept}")
        print(f"  Total after:        {after_count}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


def _reassign_skill_references(db: Session, old_id: int, new_id: int):
    """ย้าย job_skills, user_skills, recommendation_skills ไปที่ canonical skill"""

    # JobSkill — composite PK (job_id, skill_id) ต้อง check duplicate ก่อน
    for js in db.query(JobSkill).filter(JobSkill.skill_id == old_id).all():
        exists = db.query(JobSkill).filter(
            JobSkill.job_id == js.job_id,
            JobSkill.skill_id == new_id
        ).first()
        if exists:
            # เลือก importance score ที่สูงกว่า
            if (js.importance_score or 0) > (exists.importance_score or 0):
                exists.importance_score = js.importance_score
            db.delete(js)
        else:
            js.skill_id = new_id

    # UserSkill
    for us in db.query(UserSkill).filter(UserSkill.skill_id == old_id).all():
        exists = db.query(UserSkill).filter(
            UserSkill.user_id == us.user_id,
            UserSkill.skill_id == new_id
        ).first()
        if exists:
            if (us.confidence_score or 0) > (exists.confidence_score or 0):
                exists.confidence_score = us.confidence_score
            db.delete(us)
        else:
            us.skill_id = new_id

    # RecommendationSkill
    for rs in db.query(RecommendationSkill).filter(RecommendationSkill.skill_id == old_id).all():
        exists = db.query(RecommendationSkill).filter(
            RecommendationSkill.recommendation_id == rs.recommendation_id,
            RecommendationSkill.skill_id == new_id
        ).first()
        if exists:
            db.delete(rs)
        else:
            rs.skill_id = new_id

    db.flush()


def _delete_skill(db: Session, skill: Skill):
    """ลบ skill และ cascade FK"""
    db.query(JobSkill).filter(JobSkill.skill_id == skill.id).delete()
    db.query(UserSkill).filter(UserSkill.skill_id == skill.id).delete()
    db.query(RecommendationSkill).filter(RecommendationSkill.skill_id == skill.id).delete()
    db.query(SkillAlias).filter(SkillAlias.skill_id == skill.id).delete()
    db.delete(skill)
    db.flush()


if __name__ == "__main__":
    cleanup_skills()