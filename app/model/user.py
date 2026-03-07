
# from sqlalchemy import String, Enum, TIMESTAMP, func
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from typing import List

# from app.core.database import Base


# class User(Base):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
#     password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
#     first_name: Mapped[str] = mapped_column(String(100))
#     last_name: Mapped[str] = mapped_column(String(100))
#     role: Mapped[str] = mapped_column(
#         Enum("student", "admin", name="user_role_enum"),
#         default="student"
#     )
#     created_at: Mapped[str] = mapped_column(
#         TIMESTAMP, server_default=func.current_timestamp()
#     )
#     updated_at: Mapped[str] = mapped_column(
#         TIMESTAMP,
#         server_default=func.current_timestamp(),
#         onupdate=func.current_timestamp()
#     )

#     transcripts: Mapped[List["Transcript"]] = relationship(
#         back_populates="user",
#         cascade="all, delete"
#     )
#     skills: Mapped[List["UserSkill"]] = relationship(
#         back_populates="user",
#         cascade="all, delete"
#     )
#     recommendations: Mapped[List["Recommendation"]] = relationship(
#         back_populates="user",
#         cascade="all, delete"
#     )
from sqlalchemy import String, Enum, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.core.database import Base
from app.model.recommendation import Recommendation
from app.model.skill import UserSkill
from app.model.transcript import Transcript


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
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