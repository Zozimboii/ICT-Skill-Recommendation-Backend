# from datetime import datetime

# from sqlalchemy import TIMESTAMP, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, func

# from ..core.database import Base
# from sqlalchemy.orm import relationship


# class User(Base):
#     __tablename__ = "user"
#     id = Column("ID", Integer, primary_key=True, autoincrement=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#     password = Column(String(512), nullable=False)
#     create_time = Column(DateTime, server_default=func.now(), nullable=False)


# class JobPosting(Base):
#     __tablename__ = "job_postings"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     job_id = Column(Integer, unique=True, index=True)
#     title = Column(String(255))
#     link = Column(String(500), unique=True)

#     description = Column(Text)

#     posted_date = Column(Date)
#     snapshot_date = Column(Date)

#     sub_category_id = Column(Integer)
#     sub_category_name = Column(String(255))

#     main_category_id = Column(Integer)
#     main_category_name = Column(String(255))

#     created_at = Column(DateTime, server_default=func.now())
#     skills = relationship(
#         "JobSkill",
#         back_populates="job",
#         cascade="all, delete"
#     )
#     snapshots = relationship(
#         "JobSnapshot",
#         back_populates="job",
#         cascade="all, delete"
#     )

# class JobSkill(Base):
#     __tablename__ = "job_skills"

#     id = Column(Integer, primary_key=True, autoincrement=True)

#     job_id = Column(Integer, ForeignKey("job_postings.job_id"))

#     title = Column(Text)
#     skill_name = Column(Text)
#     skill_type = Column(Text)

#     created_at = Column(DateTime, default=datetime.utcnow)

#     job = relationship("JobPosting", back_populates="skills")
    
# class JobSnapshot(Base):
#     __tablename__ = "job_snapshot"

#     id = Column(Integer, primary_key=True, index=True)

#     job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    
#     job_title = Column(String(255), nullable=False)
#     sub_category_id = Column(Integer, nullable=False)
#     sub_category_name = Column(String(255), nullable=False)
#     company_name = Column(String(255))
#     snapshot_date = Column(Date, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     job = relationship("JobPosting", back_populates="snapshots")


# testtt database

# app/models.py

# from sqlalchemy import Column, BigInteger, String, Text, Date, TIMESTAMP, ForeignKey, Integer
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# from .database import Base


# class MainCategory(Base):
#     __tablename__ = "main_categories"

#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(String(255), unique=True, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     sub_categories = relationship("SubCategory", back_populates="main_category")


# class SubCategory(Base):
#     __tablename__ = "sub_categories"

#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     main_category_id = Column(BigInteger, ForeignKey("main_categories.id", ondelete="CASCADE"))
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     main_category = relationship("MainCategory", back_populates="sub_categories")
#     jobs = relationship("Job", back_populates="sub_category")


# class Job(Base):
#     __tablename__ = "jobs"

#     id = Column(BigInteger, primary_key=True, index=True)
#     external_job_id = Column(BigInteger, unique=True)
#     title = Column(Text, nullable=False)
#     link = Column(Text)
#     description = Column(Text)
#     posted_date = Column(Date)
#     sub_category_id = Column(BigInteger, ForeignKey("sub_categories.id", ondelete="CASCADE"))
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     sub_category = relationship("SubCategory", back_populates="jobs")
#     snapshots = relationship("JobSnapshot", back_populates="job")


# class JobSnapshot(Base):
#     __tablename__ = "job_snapshots"

#     id = Column(BigInteger, primary_key=True, index=True)
#     job_id = Column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"))
#     snapshot_date = Column(Date, nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     job = relationship("Job", back_populates="snapshots")


# class SnapshotSummary(Base):
#     __tablename__ = "snapshot_summary"

#     id = Column(BigInteger, primary_key=True, index=True)
#     snapshot_date = Column(Date, nullable=False)
#     main_category_id = Column(BigInteger, ForeignKey("main_categories.id", ondelete="CASCADE"))
#     sub_category_id = Column(BigInteger, ForeignKey("sub_categories.id", ondelete="CASCADE"))
#     job_count = Column(Integer, default=0)
#     created_at = Column(TIMESTAMP, server_default=func.now())

# testagign


# app/models.py

# from sqlalchemy import (
#     Column,
#     BigInteger,
#     String,
#     Text,
#     Date,
#     Boolean,
#     TIMESTAMP,
#     ForeignKey,
#     Enum,
#     UniqueConstraint
# )
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship

# from app.db.database import Base


# # ==========================
# # MAIN CATEGORY
# # ==========================

# class MainCategory(Base):
#     __tablename__ = "main_categories"

#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(String(255), nullable=False, unique=True)
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     sub_categories = relationship("SubCategory", back_populates="main_category")


# # ==========================
# # SUB CATEGORY
# # ==========================

# class SubCategory(Base):
#     __tablename__ = "sub_categories"

#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     main_category_id = Column(
#         BigInteger,
#         ForeignKey("main_categories.id", ondelete="CASCADE")
#     )
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     main_category = relationship("MainCategory", back_populates="sub_categories")
#     jobs = relationship("Job", back_populates="sub_category")


# # ==========================
# # JOBS
# # ==========================

# class Job(Base):
#     __tablename__ = "jobs"

#     id = Column(BigInteger, primary_key=True, index=True)

#     # ใช้ external_id ป้องกัน duplicate จากเว็บ
#     external_id = Column(String(255), nullable=False, unique=True)

#     title = Column(Text, nullable=False)
#     link = Column(Text)
#     description = Column(Text)
#     posted_date = Column(Date)

#     sub_category_id = Column(
#         BigInteger,
#         ForeignKey("sub_categories.id", ondelete="SET NULL"),
#         nullable=True
#     )

#     is_active = Column(Boolean, default=True)

#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(
#         TIMESTAMP,
#         server_default=func.now(),
#         onupdate=func.now()
#     )

#     sub_category = relationship("SubCategory", back_populates="jobs")
#     skills = relationship("JobSkill", back_populates="job", cascade="all, delete")
#     snapshots = relationship("JobSnapshot", back_populates="job", cascade="all, delete")


# # ==========================
# # SKILLS
# # ==========================

# class Skill(Base):
#     __tablename__ = "skills"

#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     skill_type = Column(
#         Enum("hard_skill", "soft_skill", name="skill_type_enum"),
#         nullable=False
#     )
#     created_at = Column(TIMESTAMP, server_default=func.now())

#     __table_args__ = (
#         UniqueConstraint("name", "skill_type", name="unique_skill"),
#     )

#     jobs = relationship("JobSkill", back_populates="skill", cascade="all, delete")


# # ==========================
# # JOB_SKILLS (Many-to-Many)
# # ==========================

# class JobSkill(Base):
#     __tablename__ = "job_skills"

#     id = Column(BigInteger, primary_key=True, index=True)

#     job_id = Column(
#         BigInteger,
#         ForeignKey("jobs.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     skill_id = Column(
#         BigInteger,
#         ForeignKey("skills.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     __table_args__ = (
#         UniqueConstraint("job_id", "skill_id", name="unique_job_skill"),
#     )

#     job = relationship("Job", back_populates="skills")
#     skill = relationship("Skill", back_populates="jobs")


# # ==========================
# # SNAPSHOT VERSIONING
# # ==========================

# class JobSnapshot(Base):
#     __tablename__ = "job_snapshots"

#     id = Column(BigInteger, primary_key=True, index=True)

#     snapshot_date = Column(Date, nullable=False)

#     job_id = Column(
#         BigInteger,
#         ForeignKey("jobs.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     __table_args__ = (
#         UniqueConstraint("snapshot_date", "job_id", name="unique_snapshot"),
#     )

#     job = relationship("Job", back_populates="snapshots")
