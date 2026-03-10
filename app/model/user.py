# app/model/user.py

from sqlalchemy import Boolean, String, Enum, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(
        String(50), 
        default="user"
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript",
        back_populates="user",
        cascade="all, delete"
    )
    skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill",
        back_populates="user",
        cascade="all, delete"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user",
        cascade="all, delete"
    )