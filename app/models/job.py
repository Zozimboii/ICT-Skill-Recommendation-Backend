# app/model/job.py

from sqlalchemy import Boolean, Enum, String, ForeignKey, Text, Integer, Date, TIMESTAMP, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, Optional

from app.core.database import Base



class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255))
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location:   Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    posted_date: Mapped[str] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)     

    sub_category_id: Mapped[Optional[int]] = mapped_column(
    Integer,
    ForeignKey("skill_categories.id"),
    nullable=True
)

    job_type: Mapped[Optional[str]] = mapped_column(                                # ✅ ใหม่
        Enum("full_time", "part_time", "contract", "internship", name="job_type_enum"),
        nullable=True
    )
    experience_level: Mapped[Optional[str]] = mapped_column(                        # ✅ ใหม่
        Enum("junior", "mid", "senior", "any", name="experience_level_enum"),
        nullable=True
    )
    ai_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    skills: Mapped[List["JobSkill"]] = relationship(
        back_populates="job",
        cascade="all, delete"
    )

    sub_category = relationship("SkillCategory", back_populates="jobs")
    recommendations = relationship("Recommendation", back_populates="job")


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True
    )
    importance_score: Mapped[float] = mapped_column(Float, default=0)

    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="jobs")