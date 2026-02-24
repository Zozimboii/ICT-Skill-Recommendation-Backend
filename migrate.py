"""
Migration script to update database schema
- เพิ่ม created_date, updated_date ใน job_count_by_sub_category
- สร้างตาราง job_count_history
- เพิ่มตาราง location และอัปเดต job_data table
"""

from sqlalchemy import Column, DateTime, func

from app.db.database import Base, engine
from app.db.models import (
    JobCountBySubCategory,
    JobCountHistory,
    JobSkillTrend,
    Jobs_Data,
    Location,
    User,
    JobsSkill,
    JobSkillCountBySkillname,
    JobSkillsWithCategories,
    JobSkillsWithDes,
)

# สร้างตาราง
Base.metadata.create_all(bind=engine)
print("✅ Database tables created/updated successfully!")
