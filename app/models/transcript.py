# model/transcipt.py


from sqlalchemy import String, ForeignKey, DECIMAL, TIMESTAMP, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List

from app.core.database import Base



class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    gpa: Mapped[float] = mapped_column(DECIMAL(3,2), nullable=True)
    university: Mapped[str] = mapped_column(String(255), nullable=True)
    major: Mapped[str] = mapped_column(String(255), nullable=True)
    parsed_text: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default="CURRENT_TIMESTAMP"
    )

    user = relationship("User", back_populates="transcripts")
    courses: Mapped[List["TranscriptCourse"]] = relationship(
        back_populates="transcript",
        cascade="all, delete"
    )



class TranscriptCourse(Base):
    __tablename__ = "transcript_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    transcript_id: Mapped[int] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE")
    )
    course_code: Mapped[str] = mapped_column(String(50))
    course_name: Mapped[str] = mapped_column(String(255))
    grade: Mapped[str] = mapped_column(String(5))
    credit: Mapped[float] = mapped_column(DECIMAL(3,1))

    transcript = relationship("Transcript", back_populates="courses")