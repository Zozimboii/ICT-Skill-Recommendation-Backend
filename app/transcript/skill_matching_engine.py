# app/services/transcript_match/skill_matching_engine.py
# ข้อ 5: whitelist mode — ใช้ normalize_skill ก่อน query DB ทุกครั้ง
#        ถ้า normalize คืน None → ไม่เก็บ skill นั้น

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.skill import Skill, UserSkill, SkillAlias
from app.utils.course_skill_map import COURSE_SKILL_MAP
from app.utils.canonical_skills import normalize_skill


class SkillMatchingEngine:

    def get_skill_by_name(self, db: Session, name: str) -> Skill | None:
        """case-sensitive exact match"""
        return db.execute(
            select(Skill).where(Skill.name == name)
        ).scalar_one_or_none()

    # ── Strategy 1: skill.name อยู่ใน course title ─────────────────────────

    def match_from_dictionary(self, db: Session, course_name: str) -> list[Skill]:
        if not course_name:
            return []
        course_lower = course_name.lower()
        all_skills   = db.execute(select(Skill)).scalars().all()

        seen_ids: set[int] = set()
        matched:  list[Skill] = []
        for skill in all_skills:
            if skill.id not in seen_ids and skill.name.lower() in course_lower:
                matched.append(skill)
                seen_ids.add(skill.id)
        return matched

    # ── Strategy 2: keyword → skill names จาก COURSE_SKILL_MAP ──────────────

    def match_from_course_map(self, db: Session, course_name: str) -> list[Skill]:
        if not course_name:
            return []
        course_lower    = course_name.lower()
        raw_skill_names: set[str] = set()

        for keyword, skill_names in COURSE_SKILL_MAP:
            if keyword.lower() in course_lower:
                raw_skill_names.update(skill_names)

        if not raw_skill_names:
            return []

        seen_ids: set[int] = set()
        matched:  list[Skill] = []
        for raw_name in raw_skill_names:
            # ── ข้อ 5: normalize ก่อน — ถ้า None = blocked/unknown ──────────
            canonical = normalize_skill(raw_name)
            if canonical is None:
                continue
            skill = self.get_skill_by_name(db, canonical)
            if skill and skill.id not in seen_ids:
                matched.append(skill)
                seen_ids.add(skill.id)
        return matched

    # ── Strategy 3: AI extracted skills (normalized) ──────────────────────

    def match_from_ai_skills(self, db: Session, ai_skills: list[str]) -> list[Skill]:
        if not ai_skills:
            return []
        seen_ids: set[int] = set()
        matched:  list[Skill] = []
        for raw_name in ai_skills:
            # ── ข้อ 5: normalize ก่อนเสมอ ──────────────────────────────────
            canonical = normalize_skill(raw_name)
            if canonical is None:
                continue
            skill = self.get_skill_by_name(db, canonical)
            if skill and skill.id not in seen_ids:
                matched.append(skill)
                seen_ids.add(skill.id)
        return matched

    # ── Combine strategies ────────────────────────────────────────────────────

    def match_skills(
        self,
        db: Session,
        course_name: str,
        ai_skills: list[str] | None = None,
    ) -> tuple[list[Skill], str]:
        skills = self.match_from_dictionary(db, course_name)
        if skills:
            return skills, "db_match"

        skills = self.match_from_course_map(db, course_name)
        if skills:
            return skills, "course_map"

        if ai_skills:
            skills = self.match_from_ai_skills(db, ai_skills)
            if skills:
                return skills, "ai_infer"

        return [], "none"

    def attach_user_skills(
        self,
        db: Session,
        user_id: int,
        skills: list[Skill],
        source: str,
        confidence: float,
    ):
        for skill in skills:
            db.merge(UserSkill(
                user_id=user_id,
                skill_id=skill.id,
                source=source,
                confidence_score=confidence,
            ))
        db.flush()

    def resolve_skill_by_alias(self, db: Session, raw_name: str) -> Skill | None:
        alias_key = raw_name.strip().lower()

        # 1. DB alias table
        alias_row = db.execute(
            select(SkillAlias).where(SkillAlias.alias == alias_key)
        ).scalar_one_or_none()
        if alias_row:
            return alias_row.skill

        # 2. canonical normalizer
        canonical = normalize_skill(raw_name)
        if canonical:
            skill = self.get_skill_by_name(db, canonical)
            if skill:
                return skill

        # 3. direct name
        return self.get_skill_by_name(db, raw_name.strip())