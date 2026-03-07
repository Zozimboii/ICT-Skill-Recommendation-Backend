import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal
from app.db.models import (

    JobPosting,
    JobSkill,

    JobSnapshot,
)
from app.scrapers.jobsdb_scapper import extract_job_id, fetch_jobsdb
from app.utils.category_mapping import map_category
from app.utils.skill_extractor import extract_skills
from app.utils.skill_extractor_pro import extract_skills_pro

# ----------------------------
# CONFIG
# ----------------------------
MAX_PAGES = 1
MAX_JOBS = 200


# ----------------------------
# Parse Posted Date
# ----------------------------
def parse_posted_date(text: str):
    """
    แปลงข้อความ เช่น:
    - Posted 3 days ago
    - Posted 2 months ago
    เป็นวันที่จริง
    """

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


# ----------------------------
# MAIN SCRIPT
# ----------------------------
def main():
    db = SessionLocal()

    try:
        print("🚀 Starting JobsDB Scraper...")

        # ----------------------------
        # 1) Scrape Jobs
        # ----------------------------
        all_jobs = fetch_jobsdb(max_pages=MAX_PAGES, max_jobs=MAX_JOBS)
        print("Example job:", all_jobs[:1])
        print(f"📦 Scraped {len(all_jobs)} jobs")

        snapshot_today = datetime.now().date()

        # ----------------------------
        # 2) Save into job_postings
        # ----------------------------
        inserted = 0

        for job in all_jobs:

        # ----------------------------
        # Extract Basic Data
        # ----------------------------
            title = job.get("title", "")
            link = job.get("link", "")
            description = job.get("description", "")
            posted_text = job.get("posted_at_text", "")
            # ดึงชื่อบริษัทมาด้วย (ถ้ามี) เพื่อใส่ใน Snapshot
            company_name = job.get("company_name", "N/A")

            if not title or not link:
                continue

        # ----------------------------
        # Map Category
        # ----------------------------
            cat = map_category(title)
            # if not cat:
            #     continue
            print("Category:", cat)
            if not cat:
                print(f"⚠️ Category not found for: {title}")
                continue
        # ----------------------------
        # Extract JobsDB job_id
        # ----------------------------
            job_source_id = extract_job_id(link)
            if not job_source_id:
                continue

            posted_date = parse_posted_date(posted_text)

        # ----------------------------
        # Duplicate Check
        # ----------------------------
            exists = (
                db.query(JobPosting)
                .filter(JobPosting.job_id == job_source_id)
                .first()
            )

# ----------------------------
# Case 1: Job มีอยู่แล้ว → Update Skills
# ----------------------------
            if exists:
                print(f"♻️ Updating existing job: {job_source_id}")

    # ลบ skill เก่าออกก่อน
                db.query(JobSkill).filter(
                    JobSkill.job_id == job_source_id
                ).delete()

                posting = exists

# ----------------------------
# Case 2: Job ใหม่ → Insert JobPosting
# ----------------------------
            else:
                posting = JobPosting(
                    job_id=job_source_id,
                    title=title,
                    link=link,
                    description=description,
                    posted_date=posted_date,
                    snapshot_date=snapshot_today,
                    sub_category_id=cat["sub_category_id"],
                    sub_category_name=cat["sub_category_name"],
                    main_category_id=cat["main_category_id"],
                    main_category_name=cat["main_category_name"],
                )

                db.add(posting)
                db.flush()
                print(f"✅ Inserted new job: {job_source_id}")
                
            new_snapshot = JobSnapshot(
                job_id=posting.job_id,  # เชื่อม FK ไปยัง Primary Key ของ JobPosting
                job_title=title,
                sub_category_id=cat["sub_category_id"],
                sub_category_name=cat["sub_category_name"],
                company_name=company_name,
                snapshot_date=snapshot_today
               )
            try:
                db.add(new_snapshot)
                db.flush()

                print(f"🔍 Extracting skills for job {job_source_id}...")
                skills, unknown_skills = extract_skills_pro(description)

                for skill_name, skill_type in skills:
                    new_skill = JobSkill(
                        job_id=posting.job_id,
                        title=title,
                        skill_name=skill_name,
                        skill_type=skill_type,
                        created_at=datetime.now(timezone.utc)
                    )
                db.add(new_skill)

                db.commit()
                inserted += 1

            except Exception as e:
                print("❌ Error inserting job:", e)
                db.rollback()

        # ----------------------------
        # Extract Skills
        # ----------------------------
            print(f"🔍 Extracting skills for job {job_source_id}...")
            skills, unknown_skills = extract_skills_pro(description)
            print(f"💡 Found {len(skills)} skills")
            if unknown_skills:
                print("⚠️ Unknown skills detected:")
                for u in unknown_skills[:10]:
                    print("   -", u)
                with open("unknown_skills.txt", "a", encoding="utf-8") as f:
                    for u in unknown_skills:
                        f.write(u + "\n")
        # ----------------------------
        # Insert Skills
        # ----------------------------
            for skill_name, skill_type in skills:

                new_skill = JobSkill(
                    job_id=posting.job_id,   # ✅ FK → JobsDB job_id
                    title=title,
                    skill_name=skill_name,
                    skill_type=skill_type,
                    created_at=datetime.now(timezone.utc)
                )

                db.add(new_skill)

        # ----------------------------
        # Commit Per Job
        # ----------------------------
            db.commit()
        print(f"✅ Inserted {inserted} new jobs into job_postings")

        print("\n🎉 DONE! ทุกตารางถูกอัปเดตแล้ว")

    except Exception as e:
        print("❌ ERROR:", e)
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
