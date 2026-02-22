# scripts/digest_job_skills.py
"""
Script to extract skills from job_data using Gemini API and save to job_skills_withdes table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import Jobs_Data, JobSkillsWithDes, Base
from app.services.ai_digest import extract_skills_from_job


def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables initialized")


def get_unprocessed_jobs(db: Session, limit: int = 100) -> list:
    """
    ดึง job ที่ยังไม่มี skills record ใน job_skills_withdes
    """
    # ดึง job_id ที่มี record อยู่แล้ว
    processed_job_ids = db.query(JobSkillsWithDes.job_id).distinct().all()
    processed_ids = [jid[0] for jid in processed_job_ids]
    
    # ดึง job ที่ไม่อยู่ใน processed list
    jobs = db.query(Jobs_Data).filter(
        ~Jobs_Data.id.in_(processed_ids) if processed_ids else True
    ).limit(limit).all()
    
    return jobs


def save_skills_to_db(db: Session, job_id: int, skills: dict) -> int:
    """
    บันทึก extracted skills ลง database
    
    Args:
        db: Database session
        job_id: Job ID
        skills: Dict with 'hard_skills' and 'soft_skills'
        
    Returns:
        จำนวน records ที่ถูกบันทึก
    """
    records_added = 0
    
    # Save hard skills
    for hard_skill in skills.get('hard_skills', []):
        try:
            record = JobSkillsWithDes(
                job_id=job_id,
                hard_skill=hard_skill.strip(),
                soft_skill=None
            )
            db.add(record)
            records_added += 1
        except Exception as e:
            print(f"  ⚠️ Error adding hard skill '{hard_skill}': {e}")
    
    # Save soft skills
    for soft_skill in skills.get('soft_skills', []):
        try:
            record = JobSkillsWithDes(
                job_id=job_id,
                hard_skill=None,
                soft_skill=soft_skill.strip()
            )
            db.add(record)
            records_added += 1
        except Exception as e:
            print(f"  ⚠️ Error adding soft skill '{soft_skill}': {e}")
    
    return records_added


def process_jobs(limit: int = 100):
    """
    Main function to process jobs and extract skills
    
    Args:
        limit: Maximum number of jobs to process
    """
    db = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        
        # Get unprocessed jobs
        jobs = get_unprocessed_jobs(db, limit)
        
        if not jobs:
            print("✓ All jobs have been processed!")
            return
        
        print(f"\n📊 Found {len(jobs)} unprocessed jobs")
        print("=" * 60)
        
        total_skills_added = 0
        
        for idx, job in enumerate(jobs, 1):
            print(f"\n[{idx}/{len(jobs)}] Job ID: {job.id}")
            print(f"    Title: {job.title[:70]}")
            
            # Extract skills
            skills = extract_skills_from_job(job.title, job.description or "")
            
            # Save to database
            skills_count = save_skills_to_db(db, job.id, skills)
            total_skills_added += skills_count
            
            print(f"    ✓ Added {skills_count} skills")
            print(f"      • Hard Skills ({len(skills['hard_skills'])}): {', '.join(skills['hard_skills'][:3])}")
            print(f"      • Soft Skills ({len(skills['soft_skills'])}): {', '.join(skills['soft_skills'][:3])}")
        
        # Commit all changes
        db.commit()
        print("\n" + "=" * 60)
        print(f"✅ Successfully processed {len(jobs)} jobs")
        print(f"✅ Total skills added: {total_skills_added}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract skills from job data using Gemini API")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of jobs to process")
    args = parser.parse_args()
    
    process_jobs(limit=args.limit)
