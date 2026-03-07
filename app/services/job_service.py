# backend/app/services/jobs_service.py
# from sqlalchemy import func
# from sqlalchemy.orm import Session

# from app.db.models import JobCountBySubCategory, JobsSkill


# def list_jobs(db: Session):
#     rows = (
#         db.query(JobsSkill.job_id, JobsSkill.title)
#         .group_by(JobsSkill.job_id, JobsSkill.title)
#         .limit(50)
#         .all()
#     )
#     return [{"job_id": r[0], "title": r[1]} for r in rows]


# def search_jobs(db: Session, q: str, limit: int = 20):
#     keyword = q.strip().lower()

#     matches = (
#         db.query(
#             JobCountBySubCategory.sub_category_id,
#             JobCountBySubCategory.sub_category_name,
#             JobCountBySubCategory.job_count,
#         )
#         .filter(
#             func.lower(JobCountBySubCategory.sub_category_name).like(f"%{keyword}%")
#         )
#         .order_by(JobCountBySubCategory.job_count.desc())
#         .limit(limit)
#         .all()
#     )

#     if not matches:
#         return {
#             "sub_category_id": "",
#             "sub_category_name": keyword,
#             "job_count": 0,
#             "top_categories": [],
#             "related_sub_categories": [],
#         }

#     main_sub_id, main_sub_name, main_job_count = matches[0]

#     top_categories = (
#         db.query(
#             JobCountBySubCategory.main_category_id,
#             JobCountBySubCategory.main_category_name,
#             JobCountBySubCategory.sub_category_id,
#             JobCountBySubCategory.sub_category_name,
#             JobCountBySubCategory.job_count,
#         )
#         .filter(JobCountBySubCategory.sub_category_id == main_sub_id)
#         .order_by(JobCountBySubCategory.job_count.desc())
#         .all()
#     )

#     main_category_id = top_categories[0][0] if top_categories else None

#     related = (
#         db.query(
#             JobCountBySubCategory.sub_category_id,
#             JobCountBySubCategory.sub_category_name,
#             JobCountBySubCategory.job_count,
#         )
#         .filter(JobCountBySubCategory.main_category_id == main_category_id)
#         .filter(JobCountBySubCategory.sub_category_id != main_sub_id)
#         .order_by(JobCountBySubCategory.job_count.desc())
#         .limit(10)
#         .all()
#     )

#     return {
#         "sub_category_id": int(main_sub_id),
#         "sub_category_name": main_sub_name,
#         "job_count": int(main_job_count),
#         "top_categories": [
#             {
#                 "main_category_id": r[0],
#                 "main_category_name": r[1],
#                 "sub_category_id": r[2],
#                 "sub_category_name": r[3],
#                 "job_count": int(r[4]),
#             }
#             for r in top_categories
#         ],
#         "related_sub_categories": [
#             {
#                 "sub_category_id": int(r[0]),
#                 "sub_category_name": r[1],
#                 "job_count": int(r[2]),
#             }
#             for r in related
#         ],
#     }

from datetime import datetime, timedelta
import re

from sqlalchemy import or_
from app.core.database import SessionLocal

from app.model.skill import Skill
from app.repositories.job_repository import JobRepository
from app.services.ai_service import AIService
from app.services.job_skill_service import JobSkillService
from app.services.scraper_service import ScraperService
from app.services.skill_service import SkillService
from app.utils.category_config import SUB_CATEGORY_NAMES
from app.utils.skill_dict import get_skill_dict, get_synonyms


class JobService:

    def __init__(self):
        self.scraper = ScraperService()
        self.repo = JobRepository()
        self.skill_service = SkillService()
        self.job_skill_service = JobSkillService()
        self.ai_service = AIService()

    # ──────────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────────

    def run_scraping(self, max_jobs: int = 50):
        db = SessionLocal()
        try:
            inserted = updated = skipped = 0
            page = 1
            JOBS_PER_PAGE = 50  # jobsdb แสดง ~30 job ต่อหน้า

            while inserted < max_jobs:
                print(f"\n📄 Fetching page {page}...")

                try:
                    html = self.scraper.fetch_job_list_page(page=page)
                    jobs = self.scraper.parse_job_list(html)
                except Exception as e:
                    print(f"[ERROR] fetch page {page} failed: {e}")
                    break

                if not jobs:
                    print(f"[STOP] No jobs found on page {page}")
                    break

                for job in jobs:
                    # หยุดถ้าได้ job ใหม่ครบแล้ว
                    if inserted >= max_jobs:
                        print(f"[STOP] Reached max_jobs={max_jobs}")
                        break

                    external_id = self.extract_job_id(job["detail_url"])
                    if not external_id:
                        print(f"[SKIP] Invalid URL: {job['detail_url']}")
                        continue

                    existing = self.repo.get_by_external_id(db, external_id)

                    if existing:
                        did_update = self._update_if_needed(db, existing, job)
                        if did_update:
                            updated += 1
                        else:
                            skipped += 1
                            print(f"[SKIP] Already complete: {job['title']}")
                    else:
                        self._insert_new_job(db, job, external_id)
                        inserted += 1
                        print(f"[PROGRESS] inserted={inserted}/{max_jobs}")

                page += 1

            print(f"\n✅ Done — inserted: {inserted}, updated: {updated}, skipped: {skipped}, pages: {page-1}")

        finally:
            db.close()
    # ──────────────────────────────────────────────────────────────────────────
    # INSERT: job ใหม่ที่ไม่เคยมีในระบบ
    # ──────────────────────────────────────────────────────────────────────────

    def _insert_new_job(self, db, job: dict, external_id: str):
        detail_data = self.scraper.fetch_job_detail(job["detail_url"])
        description = detail_data["description"]
        posted_text = detail_data["posted_text"]

        metadata = self.ai_service.extract_job_metadata(
            title=job["title"],
            description=description,
        )

        job_data = {
            "external_id":      external_id,
            "title":            job["title"],
            "company_name":     job["company_name"],
            "location":         job["location"],
            "description":      description,
            "salary_min":       job.get("salary_min"),
            "salary_max":       job.get("salary_max"),
            "posted_date":      self.parse_posted_date(posted_text),
            "source":           "jobsdb",
            "url":              job["detail_url"],
            # "sub_category":     metadata["sub_category"],
            "sub_category_id":  metadata.get("sub_category_id"),
            "experience_level": metadata["experience_level"],
            "job_type":         job.get("job_type"),
        }

        new_job = self.repo.create(db, job_data)
        db.commit()

        self.process_job_skills(db, new_job, description)
        db.commit()

        print(f"[INSERT] {job['title']} → {metadata['sub_category']}")

    # ──────────────────────────────────────────────────────────────────────────
    # UPDATE: job มีอยู่แล้ว แต่ข้อมูลบางส่วนยังไม่ครบ / ไม่ถูกต้อง
    # ──────────────────────────────────────────────────────────────────────────

    def _update_if_needed(self, db, existing, job: dict) -> bool:
        """
        ตรวจสอบทีละ field ว่าต้อง update ไหม
        Return True ถ้ามีการ update จริง
        """
        updates = {}
        needs_detail_fetch = False
        needs_skills = False

        # ── 1. sub_category: ว่าง หรือ ไม่อยู่ใน approved list ──────────────
        current_cat_obj = existing.sub_category
        current_cat_name = current_cat_obj.name if current_cat_obj else None

        if not current_cat_name or current_cat_name not in SUB_CATEGORY_NAMES:
            needs_detail_fetch = True   # ต้องการ description สำหรับ AI

        # ── 2. description: ว่าง ────────────────────────────────────────────
        current_desc = getattr(existing, "description", None)
        if not current_desc or len(current_desc.strip()) < 20:
            needs_detail_fetch = True

        # ── 3. skills: ยังไม่มีเลย ───────────────────────────────────────────
        skill_count = self.job_skill_service.count_skills_for_job(db, existing.id)
        if skill_count == 0:
            needs_skills = True
            needs_detail_fetch = True   # ต้องการ description

        # ── 4. salary: ว่าง แต่ scraper list มีค่า ───────────────────────────
        if existing.salary_min is None and job.get("salary_min") is not None:
            updates["salary_min"] = job["salary_min"]
            updates["salary_max"] = job.get("salary_max")

        # ── ไม่มีอะไรต้อง update เลย ─────────────────────────────────────────
        if not needs_detail_fetch and not updates:
            return False

        # ── fetch detail page (ถ้าจำเป็น) ─────────────────────────────────
        description = current_desc or ""
        if needs_detail_fetch:
            try:
                detail_data = self.scraper.fetch_job_detail(job["detail_url"])
                description = detail_data["description"] or description
                if description and len(description.strip()) >= 20:
                    updates["description"] = description
            except Exception as e:
                print(f"[WARN] Could not re-fetch detail for {job['title']}: {e}")

        # ── re-classify sub_category ─────────────────────────────────────────
        current_cat = getattr(existing, "sub_category", None)
        if not current_cat or current_cat not in SUB_CATEGORY_NAMES:
            if description:
                metadata = self.ai_service.extract_job_metadata(
                    title=job["title"],
                    description=description,
                )

                updates["sub_category_id"]  = metadata.get("sub_category_id")
                updates["experience_level"] = metadata["experience_level"]
                print(f"[UPDATE sub_category] {job['title']} → {metadata['sub_category']}")

        # ── apply updates to DB ──────────────────────────────────────────────
        if updates:
            self.repo.update(db, existing.id, updates)
            db.commit()

        # ── re-extract skills ────────────────────────────────────────────────
        if needs_skills and description:
            self.process_job_skills(db, existing, description)
            db.commit()
            print(f"[UPDATE skills] {job['title']}")

        return bool(updates) or needs_skills

    # ──────────────────────────────────────────────────────────────────────────
    # Skills processing
    # ──────────────────────────────────────────────────────────────────────────

    def process_job_skills(self, db, job, description: str):
        skills = {}  # ใช้ dict แทน list เพื่อ dedup อัตโนมัติ key=(name, type)

        # ── Source 1: Dict (รันก่อนเสมอ เร็ว ไม่เสีย quota) ─────────────────────
        for skill_name, skill_type in self.extract_skills_simple(description):
            normalized = skill_name.strip().lower()
            key = (normalized, skill_type)
            skills[key] = "dict"
        print(f"  [DICT]  found {len(skills)} skills")

        # ── Source 2: Database skills ─────────────────────────────────────────────
        before = len(skills)
        for skill_name, skill_type in self.extract_from_database(db, description):
            normalized = skill_name.strip().lower()
            key = (normalized, skill_type)
            if key not in skills:
                skills[key] = "db"
        print(f"  [DB]    added {len(skills) - before} new skills (total {len(skills)})")

        # ── Source 3: AI (เพิ่มเติมจาก 2 อันข้างบน) ──────────────────────────────
        if self.ai_service.can_call_ai():
            try:
                before = len(skills)
                ai_result = self.ai_service.extract_skills(description)
                for s in ai_result.get("hard_skills", []):
                    key = (s.strip().lower(), "hard_skill")
                    if key not in skills:
                        skills[key] = "ai"
                for s in ai_result.get("soft_skills", []):
                    key = (s.strip().lower(), "soft_skill")
                    if key not in skills:
                        skills[key] = "ai"
                print(f"  [AI]    added {len(skills) - before} new skills (total {len(skills)})")
            except Exception as e:
                print(f"  [AI ERROR] {e}")
        else:
            print(f"  [AI]    skipped — quota reached")

        print(f"  [FINAL] {len(skills)} unique skills | category_id={job.sub_category_id}")
        self._save_unique_skills(db, job, list(skills.keys()), category_id=job.sub_category_id)


    def _save_unique_skills(self, db, job, skills: list, category_id: int = None):

        for normalized, skill_type in skills:
            try:
                skill = self.skill_service.get_or_create_skill(
                    db, normalized, skill_type, category_id=category_id
                )
                self.job_skill_service.attach_skill_to_job(db, job.id, skill.id)
            except Exception as e:
                print(f"  [SAVE ERROR] '{normalized}': {e}")
        db.flush()

    # ──────────────────────────────────────────────────────────────────────────
    # Utility helpers
    # ──────────────────────────────────────────────────────────────────────────

    def extract_job_id(self, url: str) -> str | None:
        clean = url.split("#")[0].split("?")[0]
        match = re.search(r"/job/(\d+)", clean)
        return match.group(1) if match else None

    def parse_posted_date(self, text: str):
        if not text:
            return datetime.today().date()
        text = text.lower().strip()
        today = datetime.today().date()
        match = re.search(r"(\d+)", text)
        if not match:
            return today
        number = int(match.group(1))
        if any(u in text for u in ["hour", "ชม.", "minute", "นาที"]):
            return today
        if any(u in text for u in ["day", "วัน"]):
            return today - timedelta(days=number)
        if any(u in text for u in ["month", "เดือน"]):
            return today - timedelta(days=number * 30)
        return today


    def extract_skills_simple(self, description: str) -> list:
        skill_dict = get_skill_dict()
        synonyms = get_synonyms()

        found = []
        desc_lower = description.lower()

        def contains_word(word):
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            return re.search(pattern, desc_lower)

        for skill_name, skill_type in skill_dict.items():
            if contains_word(skill_name):
                found.append((skill_name, skill_type))  # ✅ แค่ 2 ค่า ไม่ต้องมี category

        for alias, real_name in synonyms.items():
            if contains_word(alias):
                skill_type = skill_dict.get(real_name)
                if skill_type:
                    found.append((real_name, skill_type))

        return list(set(found))

    def extract_from_database(self, db, description: str) -> list:
        words = description.lower().split()
        conditions = [Skill.name.ilike(f"%{w}%") for w in words[:50]]
        if not conditions:
            return []
        skills = db.query(Skill).filter(or_(*conditions)).all()
        return [(s.name, s.skill_type) for s in skills] 