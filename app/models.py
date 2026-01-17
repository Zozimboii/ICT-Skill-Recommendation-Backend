from sqlalchemy import Column, Integer, String, DateTime, Float, func
from datetime import datetime
from .database import Base

class JobsSkill(Base):
    __tablename__ = "jobs_skill"
    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    skill_name = Column(String(255), primary_key=True)  # เพราะ job_id ซ้ำได้ เลยจับคู่เป็น composite
    skill_type = Column(String(50))

class JobCountBySubCategory(Base):
    __tablename__ = "job_count_by_sub_category"
    main_category_id = Column(Integer, primary_key=True)
    main_category_name = Column(String(255))
    sub_category_id = Column(Integer, primary_key=True)
    sub_category_name = Column(String(255))
    job_count = Column(Integer)

class JobSkillCountBySkillname(Base):
    __tablename__ = "job_skill_count_by_skillname"
    skill_name = Column(String(255), primary_key=True)
    skill_type = Column(String(50))
    job_skill_count = Column(Integer)

class JobSkillsWithCategories(Base):
    __tablename__ = "job_skills_with_categories"
    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    type = Column(String(50))
    main_category_id = Column(Integer)
    main_category_name = Column(String(255))
    sub_category_id = Column(Integer)
    sub_category_name = Column(String(255))


# สำหรับเก็บ snapshot job count รายวัน/เดือน
class JobCountHistory(Base):
    __tablename__ = "job_count_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    main_category_id = Column(Integer)
    main_category_name = Column(String(255))
    sub_category_id = Column(Integer)
    sub_category_name = Column(String(255))
    job_count = Column(Integer)
    snapshot_date = Column(DateTime)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
