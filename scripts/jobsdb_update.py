#jobsdb_update.py
from app.scrapers.jobsdb_scapper import fetch_jobsdb
# from app.jobthai_scapper import fetch_jobthai
# from app.jobthaiweb_scapper import fetch_jobthaiweb
from app.utils.category_mapping import map_category
from app.db.database import SessionLocal
from app.db.models import JobCountBySubCategory, JobCountHistory
from collections import defaultdict
from datetime import datetime

db = SessionLocal()

category_count = defaultdict(int)
category_info = {}

# ดึงข้อมูลจาก 3 sources
print("Fetching jobs from JobsDB...")
jobs_jobsdb = fetch_jobsdb()

# print("Fetching jobs from JobThai...")
# jobs_jobthai = fetch_jobthai()

# print("Fetching jobs from JobThaiWeb...")
# jobs_jobthaiweb = fetch_jobthaiweb()

# รวมข้อมูลทั้งหมด
all_jobs = jobs_jobsdb
print(f"Total jobs fetched: {len(all_jobs)}")

for job in all_jobs:
    cat = map_category(job["title"])
    if not cat:
        continue

    sub_id = cat["sub_category_id"]
    category_count[sub_id] += 1
    category_info[sub_id] = cat

for sub_id, count in category_count.items():
    cat = category_info[sub_id]

    row = (
        db.query(JobCountBySubCategory)
        .filter(JobCountBySubCategory.sub_category_id == sub_id)
        .first()
    )

    if row:
        row.job_count += count
        # row.updated_date = datetime.utcnow()  # ถ้ามี field นี้ในตารางจริง
    else:
        db.add(JobCountBySubCategory(
            main_category_id=cat["main_category_id"],
            main_category_name=cat["main_category_name"],
            sub_category_id=cat["sub_category_id"],
            sub_category_name=cat["sub_category_name"],
            job_count=count,
        ))


# บันทึก snapshot ลง job_count_history
from backend.app.db.models import JobCountHistory
from datetime import datetime

snapshot_date = datetime.now().date()
for cat in db.query(JobCountBySubCategory).all():
    history = JobCountHistory(
        main_category_id=cat.main_category_id,
        main_category_name=cat.main_category_name,
        sub_category_id=cat.sub_category_id,
        sub_category_name=cat.sub_category_name,
        job_count=cat.job_count,
        snapshot_date=snapshot_date
    )
    db.add(history)
db.commit()
from sqlalchemy import func
total_jobs_in_db = db.query(
    func.sum(JobCountBySubCategory.job_count)
).scalar() or 0

print(f"📦 Total jobs in database: {total_jobs_in_db}")
db.close()
print(f"✅ Database updated and snapshot saved for {snapshot_date}!")
total_job_count = sum(category_count.values())
print(f"📊 Total jobs counted (after category mapping): {total_job_count}")


