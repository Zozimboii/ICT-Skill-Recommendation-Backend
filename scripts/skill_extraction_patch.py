# app/services/skill_extraction_patch.py
"""
HOW TO: ใช้ normalize_skill ใน skill extraction service
คัดลอก logic นี้ไปใส่ใน service ที่ทำการ extract skills จาก AI response
"""
from app.utils.canonical_skills import normalize_skill, CANONICAL_SKILLS
from app.model.skill import Skill, SkillAlias
from sqlalchemy.orm import Session


def get_or_create_canonical_skill(db: Session, raw_skill_name: str) -> Skill | None:
    """
    raw_skill_name → Skill object หรือ None ถ้า blocklist/ไม่รู้จัก

    ใช้แทน get_or_create_skill เดิมที่สร้าง skill ทุกอย่างโดยไม่กรอง
    """
    canonical_name = normalize_skill(raw_skill_name)

    if not canonical_name:
        # อยู่ใน blocklist หรือไม่รู้จัก → ไม่เก็บ
        return None

    # หาจาก DB
    skill = db.query(Skill).filter(Skill.name == canonical_name).first()

    if not skill:
        # สร้างใหม่ถ้ายังไม่มี
        skill_type = CANONICAL_SKILLS.get(canonical_name, "hard_skill")
        skill = Skill(name=canonical_name, skill_type=skill_type)
        db.add(skill)
        db.flush()

    return skill


def resolve_skill_from_alias(db: Session, raw_name: str) -> Skill | None:
    """
    ค้นหา skill จาก alias table ใน DB
    ใช้เป็น fallback หลัง normalize_skill
    """
    alias = db.query(SkillAlias).filter(
        SkillAlias.alias == raw_name.strip().lower()
    ).first()

    return alias.skill if alias else None


# ─────────────────────────────────────────────────────────────
# ตัวอย่าง: วิธีแก้ service เดิม
# ─────────────────────────────────────────────────────────────
"""
# BEFORE (สร้างทุก skill ไม่กรอง):
for skill_name in ai_extracted_skills:
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        skill = Skill(name=skill_name, skill_type="hard_skill")
        db.add(skill)

# AFTER (กรองผ่าน canonical):
for skill_name in ai_extracted_skills:
    skill = get_or_create_canonical_skill(db, skill_name)
    if skill is None:
        continue  # blocklist หรือ noise → ข้าม
    # ใช้ skill ต่อได้เลย
"""