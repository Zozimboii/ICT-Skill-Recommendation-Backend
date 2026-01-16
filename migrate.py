"""
Migration script to update database schema
- เพิ่ม created_date, updated_date ใน job_count_by_sub_category
- สร้างตาราง job_count_history
"""

from app.database import engine, Base
from app.models import JobCountBySubCategory, JobCountHistory

# สร้างตาราง
Base.metadata.create_all(bind=engine)
print("✅ Database tables created/updated successfully!")
