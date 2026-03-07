# scripts/run_scraper.py
import re
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.db.models import Job, MainCategory, SubCategory, Skill, JobSkill, JobSnapshot
from app.scrapers.run_scaper import fetch_jobsdb
from app.services.ai_skill_extractor import extract_skills_with_ai


# --- Helpers สำหรับจัดการ Relation ---

def get_or_create_sub_category(db, main_name, sub_name):
    # 1. จัดการ Main Category
    main = db.query(MainCategory).filter_by(name=main_name).first()
    if not main:
        main = MainCategory(name=main_name)
        db.add(main)
        db.flush()

    # 2. จัดการ Sub Category
    sub = db.query(SubCategory).filter_by(name=sub_name, main_category_id=main.id).first()
    if not sub:
        sub = SubCategory(name=sub_name, main_category_id=main.id)
        db.add(sub)
        db.flush()
    return sub.id

def get_or_create_skill(db, skill_name, skill_type):
    skill_name = skill_name.strip()
    skill = db.query(Skill).filter_by(name=skill_name, skill_type=skill_type).first()
    if not skill:
        skill = Skill(name=skill_name, skill_type=skill_type)
        db.add(skill)
        db.flush()
    return skill.id

def parse_posted_date(text: str):
    today = datetime.now().date()
    if not text: return today
    match = re.search(r"\d+", text.lower())
    if not match: return today
    val = int(match.group())
    if "day" in text.lower(): return today - timedelta(days=val)
    if "month" in text.lower(): return today - timedelta(days=val * 30)
    return today

# --- Main Pipeline ---

def main():
    db = SessionLocal()
    try:
        print("🚀 Starting Pipeline (Normalized Model)...")
        # 1. Scrape ข้อมูล
        all_jobs = fetch_jobsdb(max_pages=1, max_jobs=50) # ลองรันน้อยๆ ก่อน
        today = datetime.now().date()

        for j_data in all_jobs:
            ext_id = str(j_data["job_id"])
            
            # 2. จัดการ Category (ดึงค่าจากที่ Scrape หรือ AI)
            # ในที่นี้สมมติค่า Default ก่อน ถ้า Scraper คุณยังดึงไม่ได้
            sub_id = get_or_create_sub_category(db, "Information Technology", "Software Development")

            # 3. Upsert Job
            job = db.query(Job).filter_by(external_id=ext_id).first()
            if job:
                job.title = j_data["title"]
                job.description = j_data["description"]
                job.sub_category_id = sub_id
                # ลบ Skill mapping เก่าเพื่อ Update ใหม่
                db.query(JobSkill).filter_by(job_id=job.id).delete()
            else:
                job = Job(
                    external_id=ext_id,
                    title=j_data["title"],
                    link=j_data["link"],
                    description=j_data["description"],
                    posted_date=parse_posted_date(j_data["posted_at_text"]),
                    sub_category_id=sub_id
                )
                db.add(job)
            
            db.flush() # เพื่อให้ได้ job.id มาใช้ต่อ

            # 4. AI Skill Extraction
            print(f"🤖 AI Processing Skills for: {job.title[:30]}")
            skills_data = extract_skills_with_ai(job.description)

            # 5. บันทึกลงตาราง Skills และ JobSkill (Relation)
            # Hard Skills
            for s_name in skills_data.get("hard_skills", []):
                s_id = get_or_create_skill(db, s_name, "hard_skill")
                db.add(JobSkill(job_id=job.id, skill_id=s_id))
            
            # Soft Skills
            for s_name in skills_data.get("soft_skills", []):
                s_id = get_or_create_skill(db, s_name, "soft_skill")
                db.add(JobSkill(job_id=job.id, skill_id=s_id))

            # 6. บันทึก Snapshot (สำหรับหน้า Trend รายวัน)
            exists_snap = db.query(JobSnapshot).filter_by(job_id=job.id, snapshot_date=today).first()
            if not exists_snap:
                db.add(JobSnapshot(job_id=job.id, snapshot_date=today))

            db.commit() # Commit ทีละ Job เพื่อความชัวร์

        print("\n🎉 Pipeline Finished! Data is now in Database.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()