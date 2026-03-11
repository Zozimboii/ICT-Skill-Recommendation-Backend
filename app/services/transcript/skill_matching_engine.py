# # app/services/transcript_match/skill_matching_engine.py

# from sqlalchemy.orm import Session
# from sqlalchemy import select

# from app.model.skill import Skill, UserSkill
# from app.utils.course_skill_map import COURSE_SKILL_MAP


# class SkillMatchingEngine:

#     def match_from_dictionary(self, db: Session, course_name: str) -> list[Skill]:
#         """
#         Match โดยเช็คว่า skill.name อยู่ใน course_name ไหม
#         เช่น "Python" อยู่ใน "Python Programming" → match
#         """
#         if not course_name:
#             return []

#         course_lower = course_name.lower()
#         all_skills: list[Skill] = db.execute(select(Skill)).scalars().all()

#         seen_ids: set[int] = set()
#         matched: list[Skill] = []
#         for skill in all_skills:
#             if skill.id not in seen_ids and skill.name.lower() in course_lower:
#                 matched.append(skill)
#                 seen_ids.add(skill.id)

#         return matched

#     def match_from_course_map(self, db: Session, course_name: str) -> list[Skill]:
#         """
#         Match โดยใช้ COURSE_SKILL_MAP — keyword ชื่อวิชา → skill names
#         เช่น "data structures" → ["Python", "Problem Solving"]
#         ใช้เมื่อ match_from_dictionary ไม่ได้ผล (ชื่อวิชาไม่มีชื่อ skill ตรงๆ)
#         """
#         if not course_name:
#             return []

#         course_lower = course_name.lower()
#         matched_skill_names: set[str] = set()

#         for keyword, skill_names in COURSE_SKILL_MAP:
#             if keyword.lower() in course_lower:
#                 matched_skill_names.update(skill_names)

#         if not matched_skill_names:
#             return []

#         # ดึง Skill objects จาก DB
#         matched: list[Skill] = []
#         seen_ids: set[int] = set()
#         for name in matched_skill_names:
#             skill = db.execute(
#                 select(Skill).where(Skill.name == name)
#             ).scalar_one_or_none()
#             if skill and skill.id not in seen_ids:
#                 matched.append(skill)
#                 seen_ids.add(skill.id)

#         return matched

#     def match_skills(self, db: Session, course_name: str) -> tuple[list[Skill], str]:
#         """
#         รวม 2 strategy:
#         1. match_from_dictionary  (direct name match)
#         2. match_from_course_map  (keyword → skill mapping)
#         return (skills, source) โดย source = "db_match" หรือ "course_map"
#         """
#         skills = self.match_from_dictionary(db, course_name)
#         if skills:
#             return skills, "db_match"

#         skills = self.match_from_course_map(db, course_name)
#         if skills:
#             return skills, "course_map"

#         return [], "none"

#     def attach_user_skills(
#         self,
#         db: Session,
#         user_id: int,
#         skills: list[Skill],
#         source: str,
#         confidence: float
#     ):
#         for skill in skills:
#             user_skill = UserSkill(
#                 user_id=user_id,
#                 skill_id=skill.id,
#                 source=source,
#                 confidence_score=confidence
#             )
#             db.merge(user_skill)

#         db.flush()

# app/services/transcript_match/skill_matching_engine.py

# 2.
# from sqlalchemy.orm import Session
# from sqlalchemy import select

# from app.model.skill import Skill, UserSkill
# from app.utils.course_skill_map import COURSE_SKILL_MAP
# from app.utils.skill_normalizer import normalize_skill


# class SkillMatchingEngine:

#     def _get_skill_by_name(self, db: Session, name: str) -> Skill | None:
#         """ค้นหา Skill จาก DB แบบ case-insensitive"""
#         return db.execute(
#             select(Skill).where(Skill.name == name)
#         ).scalar_one_or_none()

#     def match_from_dictionary(self, db: Session, course_name: str) -> list[Skill]:
#         """
#         Strategy 1: เช็คว่า skill.name อยู่ใน course_name ไหม
#         เช่น "Python" อยู่ใน "Python Programming" → match
#         """
#         if not course_name:
#             return []

#         course_lower = course_name.lower()
#         all_skills: list[Skill] = db.execute(select(Skill)).scalars().all()

#         seen_ids: set[int] = set()
#         matched: list[Skill] = []
#         for skill in all_skills:
#             if skill.id not in seen_ids and skill.name.lower() in course_lower:
#                 matched.append(skill)
#                 seen_ids.add(skill.id)

#         return matched

#     def match_from_course_map(self, db: Session, course_name: str) -> list[Skill]:
#         """
#         Strategy 2: keyword ชื่อวิชา → skill names จาก COURSE_SKILL_MAP
#         แต่ละ skill name normalize ก่อน query DB
#         """
#         if not course_name:
#             return []

#         course_lower = course_name.lower()
#         raw_skill_names: set[str] = set()

#         for keyword, skill_names in COURSE_SKILL_MAP:
#             if keyword.lower() in course_lower:
#                 raw_skill_names.update(skill_names)

#         if not raw_skill_names:
#             return []

#         seen_ids: set[int] = set()
#         matched: list[Skill] = []

#         for raw_name in raw_skill_names:
#             # normalize → canonical name ก่อน query
#             canonical = normalize_skill(raw_name) or raw_name
#             skill = self._get_skill_by_name(db, canonical)
#             if skill and skill.id not in seen_ids:
#                 matched.append(skill)
#                 seen_ids.add(skill.id)

#         return matched

#     def match_from_ai_skills(self, db: Session, ai_skills: list[str]) -> list[Skill]:
#         """
#         Strategy 3: normalize skill names ที่ AI extract มาโดยตรง
#         เช่น AI บอกว่า "Machine Learning" → normalize → "machine learning" → query DB
#         """
#         if not ai_skills:
#             return []

#         seen_ids: set[int] = set()
#         matched: list[Skill] = []

#         for raw_name in ai_skills:
#             canonical = normalize_skill(raw_name) or raw_name.strip().lower()
#             skill = self._get_skill_by_name(db, canonical)
#             if skill and skill.id not in seen_ids:
#                 matched.append(skill)
#                 seen_ids.add(skill.id)

#         return matched

#     def match_skills(
#         self,
#         db: Session,
#         course_name: str,
#         ai_skills: list[str] | None = None
#     ) -> tuple[list[Skill], str]:
#         """
#         รวม 3 strategy:
#         1. match_from_dictionary  → direct name in course title
#         2. match_from_course_map  → keyword → skill mapping
#         3. match_from_ai_skills   → AI extracted skills (normalized)
#         return (skills, source)
#         """
#         # 1. direct
#         skills = self.match_from_dictionary(db, course_name)
#         if skills:
#             return skills, "db_match"

#         # 2. course map
#         skills = self.match_from_course_map(db, course_name)
#         if skills:
#             return skills, "course_map"

#         # 3. AI skills
#         if ai_skills:
#             skills = self.match_from_ai_skills(db, ai_skills)
#             if skills:
#                 return skills, "ai_infer"

#         return [], "none"

#     def attach_user_skills(
#         self,
#         db: Session,
#         user_id: int,
#         skills: list[Skill],
#         source: str,
#         confidence: float
#     ):
#         for skill in skills:
#             user_skill = UserSkill(
#                 user_id=user_id,
#                 skill_id=skill.id,
#                 source=source,
#                 confidence_score=confidence
#             )
#             db.merge(user_skill)
#         db.flush()

# app/services/transcript_match/skill_matching_engine.py

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.skill import Skill, UserSkill ,SkillAlias
from app.utils.course_skill_map import COURSE_SKILL_MAP
from app.utils.canonical_skills import normalize_skill

class SkillMatchingEngine:

    def _get_skill_by_name(self, db: Session, name: str) -> Skill | None:
        """ค้นหา Skill จาก DB แบบ case-insensitive"""
        return db.execute(
            select(Skill).where(Skill.name == name)
        ).scalar_one_or_none()

    def match_from_dictionary(self, db: Session, course_name: str) -> list[Skill]:
        """
        Strategy 1: เช็คว่า skill.name อยู่ใน course_name ไหม
        เช่น "Python" อยู่ใน "Python Programming" → match
        """
        if not course_name:
            return []

        course_lower = course_name.lower()
        all_skills: list[Skill] = db.execute(select(Skill)).scalars().all()

        seen_ids: set[int] = set()
        matched: list[Skill] = []
        for skill in all_skills:
            if skill.id not in seen_ids and skill.name.lower() in course_lower:
                matched.append(skill)
                seen_ids.add(skill.id)

        return matched

    def match_from_course_map(self, db: Session, course_name: str) -> list[Skill]:
        """
        Strategy 2: keyword ชื่อวิชา → skill names จาก COURSE_SKILL_MAP
        แต่ละ skill name normalize ก่อน query DB
        """
        if not course_name:
            return []

        course_lower = course_name.lower()
        raw_skill_names: set[str] = set()

        for keyword, skill_names in COURSE_SKILL_MAP:
            if keyword.lower() in course_lower:
                raw_skill_names.update(skill_names)

        if not raw_skill_names:
            return []

        seen_ids: set[int] = set()
        matched: list[Skill] = []

        for raw_name in raw_skill_names:
            # normalize → canonical name ก่อน query
            canonical = normalize_skill(raw_name) or raw_name
            skill = self._get_skill_by_name(db, canonical)
            if skill and skill.id not in seen_ids:
                matched.append(skill)
                seen_ids.add(skill.id)

        return matched

    def match_from_ai_skills(self, db: Session, ai_skills: list[str]) -> list[Skill]:
        """
        Strategy 3: normalize skill names ที่ AI extract มาโดยตรง
        เช่น AI บอกว่า "Machine Learning" → normalize → "machine learning" → query DB
        """
        if not ai_skills:
            return []

        seen_ids: set[int] = set()
        matched: list[Skill] = []

        for raw_name in ai_skills:
            canonical = normalize_skill(raw_name) or raw_name.strip().lower()
            skill = self._get_skill_by_name(db, canonical)
            if skill and skill.id not in seen_ids:
                matched.append(skill)
                seen_ids.add(skill.id)

        return matched

    def match_skills(
        self,
        db: Session,
        course_name: str,
        ai_skills: list[str] | None = None
    ) -> tuple[list[Skill], str]:
        """
        รวม 3 strategy:
        1. match_from_dictionary  → direct name in course title
        2. match_from_course_map  → keyword → skill mapping
        3. match_from_ai_skills   → AI extracted skills (normalized)
        return (skills, source)
        """
        # 1. direct
        skills = self.match_from_dictionary(db, course_name)
        if skills:
            return skills, "db_match"

        # 2. course map
        skills = self.match_from_course_map(db, course_name)
        if skills:
            return skills, "course_map"

        # 3. AI skills
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
        confidence: float
    ):
        for skill in skills:
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill.id,
                source=source,
                confidence_score=confidence
            )
            db.merge(user_skill)
        db.flush()


    # ─── Alias resolution (DB-driven) ────────────────────────────────────────

    def resolve_skill_by_alias(self, db: Session, raw_name: str) -> Skill | None:
        """
        ค้นหา Skill โดย:
        1. ตรวจ skill_aliases table ก่อน (DB-driven)
        2. fallback → skill_normalizer.py (hardcoded)
        3. fallback → direct name match
        """

        alias_key = raw_name.strip().lower()

        # 1. DB alias table
        alias_row = db.execute(
            select(SkillAlias).where(SkillAlias.alias == alias_key)
        ).scalar_one_or_none()
        if alias_row:
            return alias_row.skill

        # 2. hardcoded normalizer
        canonical = normalize_skill(raw_name)
        if canonical:
            skill = self._get_skill_by_name(db, canonical)
            if skill:
                return skill

        # 3. direct name match (case-insensitive)
        return self._get_skill_by_name(db, raw_name.strip())