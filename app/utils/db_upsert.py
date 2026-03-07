# app/utils/db_upsert.py

from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.db.models import (
    Job,
    MainCategory,
    SubCategory,
    Skill,
    JobSkill,
    JobSnapshot,
)
from app.services.ai_skill_extractor import extract_skills


def process_jobs(db, jobs):

    processed = 0
    today = datetime.utcnow().date()

    for job_data in jobs:

        external_id = str(job_data.get("job_id"))
        if not external_id:
            continue

        # ==========================
        # 1️⃣ CATEGORY (CREATE FIRST!)
        # ==========================

        main_category = job_data.get("main_category")
        sub_category = job_data.get("sub_category")

        sub_category_id = get_or_create_category(
            db,
            main_category,
            sub_category
        )

        # ==========================
        # 2️⃣ UPSERT JOB
        # ==========================

        job = (
            db.query(Job)
            .filter(Job.external_id == external_id)
            .first()
        )

        if job:
            job.title = job_data["title"]
            job.link = job_data["link"]
            job.description = job_data["description"]
            job.is_active = True
            job.sub_category_id = sub_category_id
        else:
            job = Job(
                external_id=external_id,
                title=job_data["title"],
                link=job_data["link"],
                description=job_data["description"],
                posted_date=today,
                is_active=True,
                sub_category_id=sub_category_id,
            )
            db.add(job)
            db.flush()  # เพื่อให้ได้ job.id

        # ==========================
        # 3️⃣ DELETE OLD SKILLS
        # ==========================

        db.query(JobSkill).filter(
            JobSkill.job_id == job.id
        ).delete(synchronize_session=False)

        # ==========================
        # 4️⃣ AI SKILL EXTRACTION
        # ==========================

        skill_data = extract_skills(job.description)

        hard_skills = skill_data.get("hard_skills", [])
        soft_skills = skill_data.get("soft_skills", [])

        # ==========================
        # 5️⃣ INSERT SKILLS
        # ==========================

        for name in hard_skills:
            save_skill_relation(db, job.id, name.strip(), "hard_skill")

        for name in soft_skills:
            save_skill_relation(db, job.id, name.strip(), "soft_skill")

        # ==========================
        # 6️⃣ SNAPSHOT
        # ==========================

        exists_snapshot = (
            db.query(JobSnapshot)
            .filter(
                JobSnapshot.job_id == job.id,
                JobSnapshot.snapshot_date == today,
            )
            .first()
        )

        if not exists_snapshot:
            db.add(
                JobSnapshot(
                    job_id=job.id,
                    snapshot_date=today,
                )
            )

        processed += 1

        if processed % 20 == 0:
            db.commit()
            print(f"✅ Processed {processed} jobs")

    db.commit()
    print(f"\n🎉 Finished processing {processed} jobs")


# ==========================================
# CATEGORY HELPER
# ==========================================

def get_or_create_category(db, main_name, sub_name):

    if not main_name or not sub_name:
        return None

    main = db.query(MainCategory).filter_by(name=main_name).first()

    if not main:
        main = MainCategory(name=main_name)
        db.add(main)
        db.flush()

    sub = (
        db.query(SubCategory)
        .filter_by(
            name=sub_name,
            main_category_id=main.id
        )
        .first()
    )

    if not sub:
        sub = SubCategory(
            name=sub_name,
            main_category_id=main.id,
        )
        db.add(sub)
        db.flush()

    return sub.id


# ==========================================
# SKILL HELPER
# ==========================================

def save_skill_relation(db, job_id, skill_name, skill_type):

    if not skill_name:
        return

    skill_name = skill_name.strip().lower()

    skill = (
        db.query(Skill)
        .filter(
            Skill.name == skill_name,
            Skill.skill_type == skill_type,
        )
        .first()
    )

    if not skill:
        skill = Skill(
            name=skill_name,
            skill_type=skill_type,
        )
        db.add(skill)

        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            skill = (
                db.query(Skill)
                .filter(
                    Skill.name == skill_name,
                    Skill.skill_type == skill_type,
                )
                .first()
            )

    exists = (
        db.query(JobSkill)
        .filter(
            JobSkill.job_id == job_id,
            JobSkill.skill_id == skill.id,
        )
        .first()
    )

    if not exists:
        db.add(
            JobSkill(
                job_id=job_id,
                skill_id=skill.id,
            )
        )
