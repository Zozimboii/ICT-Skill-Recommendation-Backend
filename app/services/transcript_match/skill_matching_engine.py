# app/services/skill_matching_engine.py


from sqlalchemy.orm import Session
from sqlalchemy import select

from app.model.skill import Skill, UserSkill

class SkillMatchingEngine:

    def match_from_dictionary(
        self,
        db: Session,
        course_name: str
    ) -> list[Skill]:

        if not course_name:
            return []

        course_name = course_name.lower()

        stmt = select(Skill)
        skills = db.execute(stmt).scalars().all()

        matched = []
        for skill in skills:
            if skill.name.lower() in course_name:
                matched.append(skill)

        return matched


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

        db.commit()