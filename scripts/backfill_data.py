import random
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.db.models import JobCountHistory, JobSkillTrend


def backfill():
    db = SessionLocal()
    try:
        # 1. ดึงข้อมูลต้นแบบจากวันที่ล่าสุดที่มี (2026-01-29)
        base_data = (
            db.query(JobCountHistory)
            .filter(JobCountHistory.snapshot_date == "2026-01-29")
            .all()
        )

        if not base_data:
            print("❌ ไม่พบข้อมูลต้นแบบวันที่ 2026-01-29 ในฐานข้อมูล")
            return

        print(f"🚀 เริ่มการเสกข้อมูลย้อนหลัง 60 วัน...")

        for i in range(1, 61):  # ย้อนหลัง 60 วัน
            target_date = datetime(2026, 1, 29).date() - timedelta(days=i)

            # ลบข้อมูลเก่าของวันนั้นๆ กันซ้ำ
            db.query(JobCountHistory).filter(
                JobCountHistory.snapshot_date == target_date
            ).delete()
            db.query(JobSkillTrend).filter(
                JobSkillTrend.snapshot_date == target_date
            ).delete()

            for row in base_data:
                # สุ่มจำนวนงานให้ขยับขึ้นลงนิดหน่อย (-10% ถึง +10%)
                variation = random.uniform(0.9, 1.1)
                new_count = max(1, int(row.job_count * variation))

                # บันทึก Job Count History
                db.add(
                    JobCountHistory(
                        main_category_id=row.main_category_id,
                        main_category_name=row.main_category_name,
                        sub_category_id=row.sub_category_id,
                        sub_category_name=row.sub_category_name,
                        job_count=new_count,
                        snapshot_date=target_date,
                    )
                )

                # ✅ บันทึก Job Skill Trend (แก้ปัญหาตารางว่าง)
                # สุ่ม Skill จำลองสำหรับแต่ละ Sub-Category
                mock_skills = [
                    "Python",
                    "SQL",
                    "JavaScript",
                    "Cloud",
                    "Docker",
                    "Management",
                ]
                for skill in random.sample(mock_skills, k=3):
                    db.add(
                        JobSkillTrend(
                            snapshot_date=target_date,
                            skill_name=skill,
                            sub_category_id=row.sub_category_id,
                            count=random.randint(5, 50),
                        )
                    )

            if i % 10 == 0:
                print(f"✅ บันทึกถึงวันที่ {target_date} เรียบร้อย...")

        db.commit()
        print(f"✨ สำเร็จ! ตอนนี้คุณมีข้อมูลย้อนหลัง 2 เดือนเต็มใน Database แล้ว")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
