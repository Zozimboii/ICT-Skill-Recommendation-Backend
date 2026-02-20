from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text, func

from .database import Base


class JobsSkill(Base):
    __tablename__ = "jobs_skill"
    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    skill_name = Column(
        String(255), primary_key=True
    )  # เพราะ job_id ซ้ำได้ เลยจับคู่เป็น composite
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
    snapshot_date = Column(Date)


class User(Base):
    __tablename__ = "user"
    id = Column("ID", Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(512), nullable=False)
    create_time = Column(DateTime, server_default=func.now(), nullable=False)


class JobSkillTrend(Base):
    __tablename__ = "job_skill_trend"  # หรือชื่ออื่นที่คุณต้องการ
    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(Date, index=True)
    skill_name = Column(String(255))
    sub_category_id = Column(Integer)
    count = Column(Integer)

class Jobs_Data(Base):
    __tablename__ = "job_data"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    link = Column(String(255))
    posted_at_text = Column(String(255))
    description = Column(Text, nullable=True)  # เพิ่ม description field