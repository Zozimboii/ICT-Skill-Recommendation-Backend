# app/services/job_scraper_service.py
# เปลี่ยนชื่อจาก job_service.py → job_scraper_service.py
# เปลี่ยน class JobService → JobScraperService

from datetime import datetime, timedelta
import re

from sqlalchemy import or_
from app.core.database import SessionLocal

from app.models.skill import Skill

from app.utils.category_config import SUB_CATEGORY_NAMES
from app.utils.skill_dict import get_skill_dict, get_synonyms

from app.utils.skill_normalizer import normalize
from app.ai.ai_service import AIService
from app.jobs.job_skill_service import JobSkillService
from app.jobs.jobs_repository import JobRepository
from app.scraping.scraper_service import ScraperService
from app.scraping.skill_creator_service import SkillCreatorService


class JobScraperService:

    def __init__(self):
        self.scraper = ScraperService()
        self.repo = JobRepository()
        self.skill_service = SkillCreatorService()
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

            print(f"🚀 Starting scrape — target: {max_jobs} new jobs")

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
            return inserted
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    # INSERT
    # ──────────────────────────────────────────────────────────────────────────

    def _insert_new_job(self, db, job: dict, external_id: str):
        detail_data = self.scraper.fetch_job_detail(job["detail_url"])
        description = detail_data["description"]
        posted_text = detail_data["posted_text"]
        
        metadata = self.ai_service.extract_job_metadata(
            title=job["title"],
            description=description,
        )
        sub_cat_id = metadata.get("sub_category_id")
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
            "sub_category_id":  sub_cat_id if sub_cat_id else None,
            "experience_level": metadata["experience_level"],
            "job_type":         job.get("job_type"),
        }

        new_job = self.repo.create(db, job_data)
        db.commit()

        self.process_job_skills(db, new_job, description)
        db.commit()

        print(f"[INSERT] {job['title']} → {metadata['sub_category']}")

    # ──────────────────────────────────────────────────────────────────────────
    # UPDATE
    # ──────────────────────────────────────────────────────────────────────────

    def _update_if_needed(self, db, existing, job: dict) -> bool:
        updates = {}
        needs_detail_fetch = False
        needs_skills = False

        # 1. sub_category
        current_cat_obj = existing.sub_category
        current_cat_name = current_cat_obj.name if current_cat_obj else None
        if not current_cat_name or current_cat_name not in SUB_CATEGORY_NAMES:
            needs_detail_fetch = True

        # 2. description
        current_desc = getattr(existing, "description", None)
        if not current_desc or len(current_desc.strip()) < 20:
            needs_detail_fetch = True

        # 3. skills
        skill_count = self.job_skill_service.count_skills_for_job(db, existing.id)
        if skill_count == 0:
            needs_skills = True
            needs_detail_fetch = True

        # 4. salary
        if existing.salary_min is None and job.get("salary_min") is not None:
            updates["salary_min"] = job["salary_min"]
            updates["salary_max"] = job.get("salary_max")

        if not needs_detail_fetch and not updates:
            return False

        description = current_desc or ""
        if needs_detail_fetch:
            try:
                detail_data = self.scraper.fetch_job_detail(job["detail_url"])
                description = detail_data["description"] or description
                if description and len(description.strip()) >= 20:
                    updates["description"] = description
            except Exception as e:
                print(f"[WARN] Could not re-fetch detail for {job['title']}: {e}")

        # re-classify sub_category
        current_cat_obj = existing.sub_category
        current_cat_name = current_cat_obj.name if current_cat_obj else None
        if not current_cat_name or current_cat_name not in SUB_CATEGORY_NAMES:
            if description:
                metadata = self.ai_service.extract_job_metadata(
                    title=job["title"],
                    description=description,
                )
                sub_cat_id = metadata.get("sub_category_id")
                updates["sub_category_id"]  = sub_cat_id if sub_cat_id else None  # ← 0 → None
                updates["experience_level"] = metadata["experience_level"]
                print(f"[UPDATE sub_category] {job['title']} → {metadata['sub_category']}")

        if updates:
            self.repo.update(db, existing.id, updates)
            db.commit()

        if needs_skills and description:
            self.process_job_skills(db, existing, description)
            db.commit()
            print(f"[UPDATE skills] {job['title']}")

        return bool(updates) or needs_skills

    # ──────────────────────────────────────────────────────────────────────────
    # Skills processing
    # ──────────────────────────────────────────────────────────────────────────

    def process_job_skills(self, db, job, description: str):
        skills = []

        # Priority 1: AI
        if self.ai_service.can_call_ai():
            try:
                ai_result = self.ai_service.extract_skills(description)
                for s in ai_result.get("hard_skills", []):
                    skills.append((s, "hard_skill"))
                for s in ai_result.get("soft_skills", []):
                    skills.append((s, "soft_skill"))
            except Exception as e:
                print(f"[AI ERROR] extract_skills: {e}")

        # Priority 2: Database keyword match
        if not skills:
            for skill_name, skill_type in self.extract_from_database(db, description):
                skills.append((skill_name, skill_type))

        # Priority 3: Dict fallback
        if not skills:
            for skill_name, skill_type in self.extract_skills_simple(description):
                skills.append((skill_name, skill_type))

        self._save_unique_skills(db, job, skills)

        # Log unknown skills เพื่อปรับปรุง skill_dict ในอนาคต
        from app.utils.skill_extractor_unknown import extract_skills
        _, unknown = extract_skills(description)
        if unknown:
            print(f"  [UNKNOWN SKILLS] {unknown[:10]}")

    def _save_unique_skills(self, db, job, skills: list):

        seen_names:     set[str] = set()
        seen_skill_ids: set[int] = set()

        for skill_name, skill_type, *_rest in skills:
            raw = skill_name.strip()
            if not raw:
                continue

            # normalize ก่อน — ถ้า None แปลว่า blocked/unknown
            canonical = normalize(raw)
            if canonical is None:
                continue

            if canonical in seen_names:
                continue
            seen_names.add(canonical)

            try:
                skill = self.skill_service.get_or_create_skill(db, raw, skill_type)
            except Exception as e:
                print(f"  [SKILL ERROR] '{raw}': {e}")
                db.rollback()
                continue

            if skill is None:          # ← เพิ่ม None check ตรงนี้
                continue

            if skill.id in seen_skill_ids:
                continue
            seen_skill_ids.add(skill.id)

            try:
                self.job_skill_service.attach_skill_with_auto_score(db, job, skill)
            except Exception as e:
                print(f"  [SAVE ERROR] '{skill.name}': {e}")
                db.rollback()

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
        """Fallback — ใช้ skill_dict.py จริง"""
        skill_dict = get_skill_dict()
        synonyms = get_synonyms()

        found = []
        desc_lower = description.lower()

        def contains_word(word: str) -> bool:
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            return bool(re.search(pattern, desc_lower))

        for skill_name, skill_type in skill_dict.items():
            if contains_word(skill_name):
                found.append((skill_name, skill_type))

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