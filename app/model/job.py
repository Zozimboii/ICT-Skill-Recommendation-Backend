# from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP
# from sqlalchemy.sql import func
# from app.model.base import Base

# class Job(Base):
#     __tablename__ = "jobs"

#     id = Column(Integer, primary_key=True, index=True)
#     external_id = Column(String(255), unique=True)
#     title = Column(String(255))
#     company_name = Column(String(255))
#     location = Column(String(255))
#     description = Column(Text)
#     salary_min = Column(Integer)
#     salary_max = Column(Integer)
#     posted_date = Column(Date)
#     source = Column(String(100))
#     created_at = Column(TIMESTAMP, server_default=func.now())


from sqlalchemy import Boolean, Enum, String, ForeignKey, Text, Integer, Date, TIMESTAMP, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List, Optional

from app.core.database import Base



class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    salary_min: Mapped[int] = mapped_column(Integer)
    salary_max: Mapped[int] = mapped_column(Integer)
    posted_date: Mapped[str] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)          # ✅ ใหม่
    # ✅ ใช้แค่ FK
    sub_category_id: Mapped[Optional[int]] = mapped_column(
    Integer,
    ForeignKey("skill_categories.id"),
    nullable=True
)

    # relationship
    sub_category = relationship("SkillCategory", back_populates="jobs")
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
    ai_logs: Mapped[List["AIJobLog"]] = relationship(
        back_populates="job",
        cascade="all, delete"
    )
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