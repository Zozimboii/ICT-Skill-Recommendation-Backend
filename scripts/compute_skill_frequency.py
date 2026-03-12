# scripts/compute_skill_frequency.py
"""
Phase 3 — ข้อ 9: คำนวณ frequency ของแต่ละ skill ว่าปรากฏใน % ของ jobs ทั้งหมด
รัน: python -m scripts.compute_skill_frequency

ผล: อัปเดต skills.frequency_score (0.0 – 1.0)
     0.8 = skill นี้ปรากฏใน 80% ของ jobs
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.skill import Skill
from app.models.job import JobSkill
from sqlalchemy import func


def compute_skill_frequency():
    db = SessionLocal()
    try:
        # จำนวน jobs ทั้งหมด
        total_jobs = db.query(func.count(func.distinct(JobSkill.job_id))).scalar() or 1

        print(f"Total jobs: {total_jobs}")

        # นับว่าแต่ละ skill ปรากฏใน job กี่งาน
        skill_job_counts = (
            db.query(
                JobSkill.skill_id,
                func.count(func.distinct(JobSkill.job_id)).label("job_count"),
            )
            .group_by(JobSkill.skill_id)
            .all()
        )

        updated = 0
        for skill_id, job_count in skill_job_counts:
            freq = round(job_count / total_jobs, 4)
            db.query(Skill).filter(Skill.id == skill_id).update(
                {"frequency_score": freq}
            )
            updated += 1

        db.commit()
        print(f"Updated frequency_score for {updated} skills")

        # แสดง top 20 skills
        top_skills = (
            db.query(Skill.name, Skill.frequency_score)
            .filter(Skill.frequency_score != None)
            .order_by(Skill.frequency_score.desc())
            .limit(20)
            .all()
        )
        print("\nTop 20 skills by frequency:")
        for name, freq in top_skills:
            bar = "█" * int((freq or 0) * 30)
            print(f"  {name:<30} {bar} {(freq or 0)*100:.1f}%")

    finally:
        db.close()


if __name__ == "__main__":
    compute_skill_frequency()