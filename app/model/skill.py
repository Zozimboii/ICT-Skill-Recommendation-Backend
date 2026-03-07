
from sqlalchemy import String, Enum, ForeignKey, TIMESTAMP, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, Optional

from app.core.database import Base



class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    skills: Mapped[List["Skill"]] = relationship(back_populates="category")
    # relationship
    jobs = relationship("Job", back_populates="sub_category")

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    skill_type: Mapped[str] = mapped_column(
        Enum("hard_skill", "soft_skill", name="skill_type_enum")
    )
    category_id: Mapped[Optional[int]] = mapped_column(  # ✅ nullable
        ForeignKey("skill_categories.id"),
        nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    category = relationship("SkillCategory", back_populates="skills")
    users = relationship("UserSkill", back_populates="skill")
    jobs = relationship("JobSkill", back_populates="skill")


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True
    )
    source: Mapped[str] = mapped_column(
        Enum("transcript", "assessment", "ai", name="user_skill_source_enum")
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0)

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="users")