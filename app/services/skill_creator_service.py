# # app/services/skill_service.py

# from sqlalchemy.orm import Session
# from app.model.skill import Skill


# class SkillCreatorService:
#     def get_or_create_skill(
#         self,
#         db: Session,
#         name: str,
#         skill_type: str,
#     ) -> Skill:
#         name = name.strip().lower()

#         existing = db.query(Skill).filter(Skill.name == name).first()
#         if existing:
#             print(f"    [SKILL] existing: id={existing.id} name='{existing.name}'")
#             return existing

#         skill = Skill(
#             name=name,
#             skill_type=skill_type,

#         )
#         db.add(skill)
#         db.flush() 
#         print(f"    [SKILL] created: id={skill.id} name='{skill.name}'")
#         return skill
# app/services/skill_creator_service.py
from sqlalchemy.orm import Session

from app.model.skill import Skill, SkillAlias
from app.utils.skill_normalizer import normalize, CANONICAL_SKILLS


class SkillCreatorService:

    def get_or_create_skill(
        self,
        db: Session,
        name: str,
        skill_type: str,
    ) -> Skill | None:
        """
        raw name → normalize → lookup/create Skill
        returns None ถ้า skill ถูก block หรือไม่รู้จัก
        """

        # ── Step 1: Normalize ────────────────────────────────────
        canonical_name = normalize(name)

        if canonical_name is None:
            print(f"    [SKILL BLOCKED/UNKNOWN] '{name}' → skip")
            return None

        # ── Step 2: Lookup DB by canonical name ──────────────────
        skill = db.query(Skill).filter(Skill.name == canonical_name).first()
        if skill:
            print(f"    [SKILL] existing: id={skill.id} '{skill.name}'")
            return skill

        # ── Step 3: Lookup alias table (safety fallback) ─────────
        alias_row = db.query(SkillAlias).filter(
            SkillAlias.alias == canonical_name.lower()
        ).first()
        if alias_row:
            print(f"    [SKILL] alias found: '{name}' → '{alias_row.skill.name}'")
            return alias_row.skill

        # ── Step 4: Create canonical skill ───────────────────────
        # ใช้ skill_type จาก CANONICAL_SKILLS ถ้ามี ไม่งั้นใช้ที่ส่งมา
        resolved_type = CANONICAL_SKILLS.get(canonical_name, skill_type)
        skill = Skill(name=canonical_name, skill_type=resolved_type)
        db.add(skill)
        db.flush()

        # เพิ่ม alias สำหรับ raw name ด้วย (ป้องกัน duplicate ในอนาคต)
        raw_lower = name.strip().lower()
        if raw_lower != canonical_name.lower():
            existing_alias = db.query(SkillAlias).filter(
                SkillAlias.alias == raw_lower
            ).first()
            if not existing_alias:
                db.add(SkillAlias(alias=raw_lower, skill_id=skill.id))
                db.flush()

        print(f"    [SKILL] created: id={skill.id} '{canonical_name}' (from '{name}')")
        return skill