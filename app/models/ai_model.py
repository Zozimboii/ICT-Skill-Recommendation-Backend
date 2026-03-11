# model/ai_model.py


from sqlalchemy import String, ForeignKey, TIMESTAMP, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base




class AIModel(Base):
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )


class AIJobLog(Base):
    __tablename__ = "ai_job_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE")
    )
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ai_models.id")
    )
    raw_response: Mapped[dict] = mapped_column(JSON)
    processed_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    token_used: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50))

    job = relationship("Job", back_populates="ai_logs")


class AITranscriptLog(Base):
    __tablename__ = "ai_transcript_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    transcript_id: Mapped[int] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE")
    )
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ai_models.id")
    )
    raw_response: Mapped[dict] = mapped_column(JSON)
    processed_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )
    token_used: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50))

    transcript = relationship("Transcript", back_populates="ai_logs")