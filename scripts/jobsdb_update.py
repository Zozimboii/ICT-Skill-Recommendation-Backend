import re
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import func
from app.scrapers.jobsdb_scapper import fetch_jobsdb
from app.utils.category_mapping import map_category
from app.db.database import SessionLocal
from app.db.models import JobCountBySubCategory, JobCountHistory, JobSkillTrend

MAX_PAGES = 100
MAX_JOBS = 5000


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
        all_jobs = fetch_jobsdb(max_pages=MAX_PAGES, max_jobs=MAX_JOBS)
        print(f"📦 Processing {len(all_jobs)} jobs for historical distribution...")

        for job in all_jobs:
            cat = map_category(job.get("title", ""))
            if not cat:
                continue

            sub_id = cat["sub_category_id"]
            category_info[sub_id] = cat

            # ✅ คำนวณวันจริงที่ลงประกาศ
            actual_date = parse_posted_date(job.get("posted_at_text", ""))

            # เก็บยอดลงในวันที่นั้นๆ (ย้อนหลัง)
            daily_history[actual_date][sub_id] += 1

            # เก็บ Skill สำหรับ Sankey ย้อนหลัง
            for skill in cat.get("skills", []):
                daily_skills[actual_date][(skill, sub_id)] += 1

        print(f"💾 Updating database for {len(daily_history)} unique dates...")

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
        print(
            f"✅ Historical backfill complete. Check database for multiple snapshot_dates."
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
