# scripts/jobsdb_update.py
from collections import defaultdict
from datetime import datetime
from sqlalchemy import func

from app.scrapers.jobsdb_scapper import fetch_jobsdb
from app.utils.category_mapping import map_category
from app.db.database import SessionLocal
from app.db.models import JobCountBySubCategory, JobCountHistory

MAX_PAGES = 30      # ✅ ปรับได้ เช่น 20-50
MAX_JOBS = 1500     # ✅ กันเหนียว เผื่อบางหน้ามี error แต่ยังไปต่อ

def main():
    db = SessionLocal()
    try:
        category_count = defaultdict(int)
        category_info = {}

        # -------------------------
        # Fetch jobs
        # -------------------------
        print("Fetching jobs from JobsDB...")
        all_jobs = fetch_jobsdb(max_pages=MAX_PAGES, max_jobs=MAX_JOBS)

        print(f"Total jobs fetched: {len(all_jobs)}")

        # -------------------------
        # Aggregate by sub-category
        # -------------------------
        for job in all_jobs:
            title = (job.get("title") or "").strip()
            if not title:
                continue

            cat = map_category(title)
            if not cat:
                continue

            sub_id = cat["sub_category_id"]
            category_count[sub_id] += 1
            category_info[sub_id] = cat

        print(f"Total jobs counted (after mapping): {sum(category_count.values())}")

        # -------------------------
        # Update JobCountBySubCategory (✅ SET ไม่ใช่ +=)
        # -------------------------
        for sub_id, count in category_count.items():
            cat = category_info[sub_id]

            row = (
                db.query(JobCountBySubCategory)
                .filter(JobCountBySubCategory.sub_category_id == sub_id)
                .first()
            )

            if row:
                row.main_category_id = cat["main_category_id"]
                row.main_category_name = cat["main_category_name"]
                row.sub_category_name = cat["sub_category_name"]
                row.job_count = count  # ✅ สำคัญ: ไม่บวกทับ
            else:
                db.add(
                    JobCountBySubCategory(
                        main_category_id=cat["main_category_id"],
                        main_category_name=cat["main_category_name"],
                        sub_category_id=cat["sub_category_id"],
                        sub_category_name=cat["sub_category_name"],
                        job_count=count,
                    )
                )

        db.commit()

        # -------------------------
        # Snapshot → JobCountHistory
        # -------------------------
        snapshot_date = datetime.now().date()

        # (ทางเลือก) กัน snapshot ซ้ำวันเดียวกัน: ลบทิ้งก่อนแล้วค่อย insert ใหม่
        db.query(JobCountHistory).filter(JobCountHistory.snapshot_date == snapshot_date).delete()
        db.commit()

        for cat in db.query(JobCountBySubCategory).all():
            db.add(
                JobCountHistory(
                    main_category_id=cat.main_category_id,
                    main_category_name=cat.main_category_name,
                    sub_category_id=cat.sub_category_id,
                    sub_category_name=cat.sub_category_name,
                    job_count=cat.job_count,
                    snapshot_date=snapshot_date,
                )
            )

        db.commit()

        # -------------------------
        # Summary
        # -------------------------
        total_jobs_in_db = db.query(func.sum(JobCountBySubCategory.job_count)).scalar() or 0
        print(f"📦 Total jobs in database: {total_jobs_in_db}")
        print(f"✅ Database updated and snapshot saved for {snapshot_date}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
