
from sqlalchemy import ForeignKey, Float, TIMESTAMP, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE")
    )
    match_score: Mapped[float] = mapped_column(Float)
    skill_match_percent: Mapped[float] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    user = relationship("User", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")
    skills = relationship(
        "RecommendationSkill",
        back_populates="recommendation",
        cascade="all, delete"
    )


class RecommendationSkill(Base):
    __tablename__ = "recommendation_skills"

    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True
    )
    match_type: Mapped[str] = mapped_column(
        Enum("matched", "missing", name="recommendation_match_enum")
    )

    recommendation = relationship(
        "Recommendation",
        back_populates="skills"
    )