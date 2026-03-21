# scripts/reprocess_skills.py
"""
Re-extract skills สำหรับ jobs ที่มีอยู่ใน DB ด้วย structured extractor ใหม่

Usage:
  py -m scripts.reprocess_skills              ← re-process ทุก job
  py -m scripts.reprocess_skills --limit 50   ← แค่ 50 jobs แรก
  py -m scripts.reprocess_skills --no-skills-only ← เฉพาะ jobs ที่ไม่มี skills

ลำดับการรัน:
  1. py -m scripts.seed_skill_aliases      (seed canonical skills)
  2. py -m scripts.reprocess_skills        (re-extract skills)
  3. py -m scripts.compute_skill_frequency (คำนวณ frequency ใหม่)
"""
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.job import Job, JobSkill
from app.models.skill import Skill
from app.models.recommendation import RecommendationSkill
from app.ai.ai_skill_extractor import AISkillExtractor
from app.scraping.skill_creator_service import SkillCreatorService
from app.jobs.job_skill_service import JobSkillService
from sqlalchemy import func


def reprocess_skills(limit: int | None = None, no_skills_only: bool = False):
    db = SessionLocal()
    extractor     = AISkillExtractor()
    skill_svc     = SkillCreatorService()
    job_skill_svc = JobSkillService()

    try:
        query = db.query(Job)

        if no_skills_only:
            # เฉพาะ jobs ที่ยังไม่มี skills
            jobs_with_skills = db.query(JobSkill.job_id).distinct()
            query = query.filter(Job.id.notin_(jobs_with_skills))
            print(f"Mode: jobs ที่ยังไม่มี skills")
        else:
            print(f"Mode: re-process ทุก job")

        if limit:
            query = query.limit(limit)

        jobs = query.all()
        print(f"Jobs to process: {len(jobs)}\n")

        success = 0
        failed  = 0

        for i, job in enumerate(jobs, 1):
            if not job.description or len(job.description.strip()) < 50:
                print(f"[SKIP] {job.title} — no description")
                continue

            print(f"[{i}/{len(jobs)}] {job.title}")

            try:
                # ลบ skills เก่าของ job นี้ก่อน
                db.query(JobSkill).filter(JobSkill.job_id == job.id).delete()
                db.flush()

                # extract ใหม่
                extracted = extractor.extract_skills_structured(
                    title=job.title,
                    description=job.description,
                )

                seen_ids: set[int] = set()
                saved = 0

                for item in extracted:
                    skill = skill_svc.get_or_create_skill(
                        db, item["skill_name"], item["skill_type"]
                    )
                    if skill is None or skill.id in seen_ids:
                        continue
                    seen_ids.add(skill.id)

                    job_skill_svc.attach_skill_with_score(
                        db, job, skill, item["importance_score"]
                    )
                    saved += 1

                db.commit()
                print(f"  → {saved} skills saved")
                success += 1

            except Exception as e:
                db.rollback()
                print(f"  ❌ Error: {e}")
                failed += 1

        print(f"\n{'='*50}")
        print(f"Done: success={success}  failed={failed}")
        print(f"\nNext steps:")
        print(f"  py -m scripts.compute_skill_frequency")
        print(f"  (re-generate recommendations for all users)")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit",          type=int, default=None)
    parser.add_argument("--no-skills-only", action="store_true")
    args = parser.parse_args()

    reprocess_skills(
        limit=args.limit,
        no_skills_only=args.no_skills_only,
    )