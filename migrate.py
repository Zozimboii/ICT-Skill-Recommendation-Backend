"""
Migration script to update database schema
- เพิ่ม created_date, updated_date ใน job_count_by_sub_category
- สร้างตาราง job_count_history
"""

from app.db.database import engine, Base
from app.db.models import JobCountBySubCategory, JobCountHistory ,User
from sqlalchemy import Column, DateTime, func

# สร้างตาราง
Base.metadata.create_all(bind=engine)
print("✅ Database tables created/updated successfully!")
