
# app/model/skill.py

from sqlalchemy import String, Enum, TIMESTAMP, func, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.core.database import Base


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    jobs = relationship("Job", back_populates="sub_category")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    skill_type: Mapped[str] = mapped_column(
        Enum("hard_skill", "soft_skill", name="skill_type_enum")
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    frequency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    users    = relationship("UserSkill",  back_populates="skill")
    jobs     = relationship("JobSkill",   back_populates="skill")
    aliases  = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")


class SkillAlias(Base):
    """
    alias (lowercase) → canonical Skill
    เช่น "postgresql" → Skill(name="postgres")
         "amazon web services" → Skill(name="aws")
    Admin เพิ่ม alias เองได้โดยไม่ต้องแก้ code
    """
    __tablename__ = "skill_aliases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)  # lowercase เสมอ
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    skill = relationship("Skill", back_populates="aliases")


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

    user  = relationship("User",  back_populates="skills")
    skill = relationship("Skill", back_populates="users")