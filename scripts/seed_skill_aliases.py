# scripts/seed_skill_aliases.py
"""
Seed canonical skills + aliases เข้า DB
รัน: python -m scripts.seed_skill_aliases

ควรรันก่อน cleanup_skills และรันทุกครั้งที่เพิ่ม canonical skill ใหม่
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.skill import Skill, SkillAlias
from app.utils.canonical_skills import CANONICAL_SKILLS, SKILL_ALIASES


def seed():
    db = SessionLocal()
    try:
        created_skills = 0
        created_aliases = 0
        updated = 0

        # ── 1. Upsert canonical skills ──────────────────────────
        for name, skill_type in CANONICAL_SKILLS.items():
            skill = db.query(Skill).filter(Skill.name == name).first()
            if not skill:
                skill = Skill(name=name, skill_type=skill_type)
                db.add(skill)
                created_skills += 1
            else:
                # fix skill_type ถ้าผิด
                if skill.skill_type != skill_type:
                    skill.skill_type = skill_type
                    updated += 1

        db.flush()

        # ── 2. Upsert aliases ───────────────────────────────────
        for alias_name, canonical_name in SKILL_ALIASES.items():
            canonical_skill = db.query(Skill).filter(
                Skill.name == canonical_name
            ).first()

            if not canonical_skill:
                print(f"  WARN: canonical '{canonical_name}' not found, skipping alias '{alias_name}'")
                continue

            existing = db.query(SkillAlias).filter(
                SkillAlias.alias == alias_name.lower()
            ).first()

            if not existing:
                db.add(SkillAlias(
                    alias=alias_name.lower(),
                    skill_id=canonical_skill.id,
                ))
                created_aliases += 1

        db.commit()

        total_skills = db.query(Skill).count()
        total_aliases = db.query(SkillAlias).count()

        print(f"\nSeed complete:")
        print(f"  Created skills:  {created_skills}")
        print(f"  Updated skills:  {updated}")
        print(f"  Created aliases: {created_aliases}")
        print(f"  Total skills:    {total_skills}")
        print(f"  Total aliases:   {total_aliases}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()