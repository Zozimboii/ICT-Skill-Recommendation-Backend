import re
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import func
from app.scrapers.jobsdb_scapper import fetch_jobsdb
from app.utils.category_mapping import map_category
from app.db.database import SessionLocal
from app.db.models import JobCountBySubCategory, JobCountHistory, JobSkillTrend, Jobs_Data, Location

MAX_PAGES = 5
MAX_JOBS = 100
FETCH_JOB_DETAILS = False

def parse_posted_date(text):
    """คำนวณวันย้อนหลังจากข้อความ 'Posted 5 days ago'"""
    today = datetime.now().date()
    if not text:
        return today

    text = text.lower()
    match = re.search(r"\d+", text)
    if not match:
        return today
    value = int(match.group())

    if "day" in text:
        return today - timedelta(days=value)
    if "month" in text:
        return today - timedelta(days=value * 30)
    return today

def main():
    db = SessionLocal()
    try:
        # แยกเก็บข้อมูลรายวันตามจริง
        daily_history = defaultdict(lambda: defaultdict(int))
        daily_skills = defaultdict(lambda: defaultdict(int))
        category_info = {}

        print("🚀 Starting scraper...")
        all_jobs = fetch_jobsdb(max_pages=MAX_PAGES, max_jobs=MAX_JOBS, fetch_details=FETCH_JOB_DETAILS)
        print(f"\n✅ Scraper got {len(all_jobs)} jobs")
        
        if len(all_jobs) == 0:
            print("❌ ERROR: Scraper returned 0 jobs!")
            return

        # บันทึกข้อมูลงานทั้งหมดลง job_data table
        print(f"\n💾 Saving raw job data to job_data table...")
        db.query(Jobs_Data).delete()
        
        for job in all_jobs:
            location_name = job.get("location", "").strip()
            location_id = None
            
            # หากมี location ให้หาหรือสร้าง Location record
            if location_name:
                location = db.query(Location).filter(Location.name == location_name).first()
                if not location:
                    location = Location(name=location_name)
                    db.add(location)
                    db.flush()  # flush to get the location.id
                location_id = location.id
            
            job_data = Jobs_Data(
                title=job.get("title", ""),
                link=job.get("link", ""),
                posted_at_text=job.get("posted_at_text", ""),
                description=job.get("description", ""),
                location_id=location_id
            )
            db.add(job_data)
        
        db.commit()
        print(f"   ✅ Saved {len(all_jobs)} jobs to job_data table")
        print(f"\n📦 Processing {len(all_jobs)} jobs for categorization...")

        # Show first 3 jobs
        print("\n📋 First 3 jobs from scraper:")
        for i, job in enumerate(all_jobs[:3], 1):
            print(f"   {i}. Title: {job.get('title', 'N/A')[:60]}")
            print(f"      Posted: {job.get('posted_at_text', 'N/A')}")

        successful_categorized = 0
        failed_categorized = []
        
        for job in all_jobs:
            title = job.get("title", "")
            posted_text = job.get("posted_at_text", "")
            
            cat = map_category(title)
            if not cat:
                failed_categorized.append(title)
                continue

            successful_categorized += 1
            sub_id = cat["sub_category_id"]
            category_info[sub_id] = cat

            # ✅ คำนวณวันจริงที่ลงประกาศ
            actual_date = parse_posted_date(posted_text)

            # เก็บยอดลงในวันที่นั้นๆ (ย้อนหลัง)
            daily_history[actual_date][sub_id] += 1

            # เก็บ Skill สำหรับ Sankey ย้อนหลัง
            for skill in cat.get("skills", []):
                daily_skills[actual_date][(skill, sub_id)] += 1

        print(f"\n✅ Successfully categorized: {successful_categorized}")
        print(f"❌ Failed to categorize: {len(failed_categorized)}")
        
        if failed_categorized:
            print(f"\n❓ Sample uncategorized titles:")
            for title in failed_categorized[:5]:
                print(f"   - {title}")

        if successful_categorized == 0:
            print("\n⚠️ WARNING: No jobs were categorized! Cannot save to database.")
            return

        print(f"\n💾 Updating database for {len(daily_history)} unique dates...")
        print(f"   Categories found: {len(category_info)}")

        # 1. จัดการตาราง History และ Skill Trend ย้อนหลัง
        for target_date in daily_history.keys():
            # ลบข้อมูลเก่าเฉพาะวันที่เรากำลังจะ Insert เพื่อป้องกันข้อมูลซ้ำ
            db.query(JobCountHistory).filter(
                JobCountHistory.snapshot_date == target_date
            ).delete()
            db.query(JobSkillTrend).filter(
                JobSkillTrend.snapshot_date == target_date
            ).delete()

            for sub_id, count in daily_history[target_date].items():
                c = category_info[sub_id]
                db.add(
                    JobCountHistory(
                        main_category_id=c["main_category_id"],
                        main_category_name=c["main_category_name"],
                        sub_category_id=sub_id,
                        sub_category_name=c["sub_category_name"],
                        job_count=count,
                        snapshot_date=target_date,
                    )
                )

            for (skill, sub_id), count in daily_skills[target_date].items():
                db.add(
                    JobSkillTrend(
                        snapshot_date=target_date,
                        skill_name=skill,
                        sub_category_id=sub_id,
                        count=count,
                    )
                )

        db.commit()
        print(f"   ✅ JobCountHistory and JobSkillTrend saved")

        # 2. อัปเดตตาราง JobCountBySubCategory (ยอดล่าสุด ณ ปัจจุบัน)
        # วิธีการคือรวมยอดจากทุกวันที่ดึงมาได้ใหม่
        db.query(JobCountBySubCategory).delete()
        for sub_id, c in category_info.items():
            total_latest = sum(daily_history[d][sub_id] for d in daily_history)
            db.add(
                JobCountBySubCategory(
                    main_category_id=c["main_category_id"],
                    main_category_name=c["main_category_name"],
                    sub_category_id=sub_id,
                    sub_category_name=c["sub_category_name"],
                    job_count=total_latest,
                )
            )

        db.commit()
        print(f"   ✅ JobCountBySubCategory updated")
        print(
            f"\n✅ SUCCESS! Database updated with job data."
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
