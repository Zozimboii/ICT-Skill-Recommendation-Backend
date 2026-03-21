# # app/services/job_scraper_service.py
# # ข้อ 5: ไม่ add skill ที่ไม่รู้จัก → ใช้ normalize() กรองก่อนเสมอ
# # ข้อ 3: skill grouping ดีขึ้น → ผ่าน SkillCreatorService ที่ใช้ canonical_skills

# from datetime import datetime, timedelta
# import re

# from sqlalchemy import or_
# from app.core.database import SessionLocal

# from app.models.skill import Skill

# from app.utils.category_config import SUB_CATEGORY_NAMES
# from app.utils.skill_normalizer import normalize  # ← single source of truth
# from app.ai.ai_service import AIService
# from app.jobs.job_skill_service import JobSkillService
# from app.jobs.jobs_repository import JobRepository
# from app.scraping.scraper_service import ScraperService
# from app.scraping.skill_creator_service import SkillCreatorService


# class JobScraperService:

#     def __init__(self):
#         self.scraper        = ScraperService()
#         self.repo           = JobRepository()
#         self.skill_service  = SkillCreatorService()
#         self.job_skill_svc  = JobSkillService()
#         self.ai_service     = AIService()

#     # ── Main entry point ──────────────────────────────────────────────────────

#     def run_scraping(self, max_jobs: int = 50):
#         db = SessionLocal()
#         try:
#             inserted = updated = skipped = 0
#             page = 1

#             print(f"🚀 Starting scrape — target: {max_jobs} new jobs")

#             while inserted < max_jobs:
#                 print(f"\n📄 Fetching page {page}...")
#                 try:
#                     html = self.scraper.fetch_job_list_page(page=page)
#                     jobs = self.scraper.parse_job_list(html)
#                 except Exception as e:
#                     print(f"[ERROR] fetch page {page} failed: {e}")
#                     break

#                 if not jobs:
#                     print(f"[STOP] No jobs on page {page}")
#                     break

#                 for job in jobs:
#                     if inserted >= max_jobs:
#                         break

#                     external_id = self.extract_job_id(job["detail_url"])
#                     if not external_id:
#                         continue

#                     existing = self.repo.get_by_external_id(db, external_id)
#                     if existing:
#                         did_update = self._update_if_needed(db, existing, job)
#                         updated += did_update
#                         skipped += not did_update
#                     else:
#                         self._insert_new_job(db, job, external_id)
#                         inserted += 1
#                         print(f"[PROGRESS] inserted={inserted}/{max_jobs}")

#                 page += 1

#             print(f"\n✅ Done — inserted:{inserted} updated:{updated} skipped:{skipped}")
#             return inserted
#         finally:
#             db.close()

#     # ── INSERT ────────────────────────────────────────────────────────────────

#     def _insert_new_job(self, db, job: dict, external_id: str):
#         detail_data = self.scraper.fetch_job_detail(job["detail_url"])
#         description = detail_data["description"]
#         posted_text = detail_data["posted_text"]

#         metadata = self.ai_service.extract_job_metadata(
#             title=job["title"],
#             description=description,
#         )
#         sub_cat_id = metadata.get("sub_category_id") or None

#         job_data = {
#             "external_id":      external_id,
#             "title":            job["title"],
#             "company_name":     job["company_name"],
#             "location":         job["location"],
#             "description":      description,
#             "salary_min":       job.get("salary_min"),
#             "salary_max":       job.get("salary_max"),
#             "posted_date":      self.parse_posted_date(posted_text),
#             "source":           "jobsdb",
#             "url":              job["detail_url"],
#             "sub_category_id":  sub_cat_id,
#             "experience_level": metadata["experience_level"],
#             "job_type":         job.get("job_type"),
#         }

#         new_job = self.repo.create(db, job_data)
#         db.commit()

#         self.process_job_skills(db, new_job, description)
#         db.commit()
#         print(f"[INSERT] {job['title']} → {metadata['sub_category']}")

#     # ── UPDATE ────────────────────────────────────────────────────────────────

#     def _update_if_needed(self, db, existing, job: dict) -> bool:
#         updates        = {}
#         needs_detail   = False
#         needs_skills   = False

#         current_cat    = existing.sub_category
#         current_cat_nm = current_cat.name if current_cat else None
#         current_desc   = getattr(existing, "description", None) or ""

#         if not current_cat_nm or current_cat_nm not in SUB_CATEGORY_NAMES:
#             needs_detail = True
#         if len(current_desc.strip()) < 20:
#             needs_detail = True
#         if self.job_skill_svc.count_skills_for_job(db, existing.id) == 0:
#             needs_skills = True
#             needs_detail = True

#         if existing.salary_min is None and job.get("salary_min") is not None:
#             updates["salary_min"] = job["salary_min"]
#             updates["salary_max"] = job.get("salary_max")

#         if not needs_detail and not updates:
#             return False

#         description = current_desc
#         if needs_detail:
#             try:
#                 detail = self.scraper.fetch_job_detail(job["detail_url"])
#                 description = detail["description"] or description
#                 if len(description.strip()) >= 20:
#                     updates["description"] = description
#             except Exception as e:
#                 print(f"[WARN] re-fetch failed for {job['title']}: {e}")

#         current_cat_nm = existing.sub_category.name if existing.sub_category else None
#         if not current_cat_nm or current_cat_nm not in SUB_CATEGORY_NAMES:
#             if description:
#                 meta = self.ai_service.extract_job_metadata(
#                     title=job["title"], description=description
#                 )
#                 updates["sub_category_id"]  = meta.get("sub_category_id") or None
#                 updates["experience_level"] = meta["experience_level"]

#         if updates:
#             self.repo.update(db, existing.id, updates)
#             db.commit()

#         if needs_skills and description:
#             self.process_job_skills(db, existing, description)
#             db.commit()

#         return bool(updates) or needs_skills

#     # ── Skills processing ─────────────────────────────────────────────────────

#     def process_job_skills(self, db, job, description: str):
#         """
#         ข้อ 5: ทุก path ผ่าน normalize() ก่อนเสมอ
#         ถ้า normalize คืน None → ไม่เก็บ (blocked / unknown)
#         """
#         skills: list[tuple[str, str]] = []

#         # Priority 1: AI extraction
#         if self.ai_service.can_call_ai():
#             try:
#                 ai_result = self.ai_service.extract_skills(description)
#                 for s in ai_result.get("hard_skills", []):
#                     skills.append((s, "hard_skill"))
#                 for s in ai_result.get("soft_skills", []):
#                     skills.append((s, "soft_skill"))
#             except Exception as e:
#                 print(f"[AI ERROR] extract_skills: {e}")

#         # Priority 2: DB keyword match (fallback)
#         if not skills:
#             skills = self._extract_from_db(db, description)

#         # Priority 3: dict fallback
#         if not skills:
#             skills = self._extract_simple(description)

#         self._save_skills(db, job, skills)

#         # log unknowns
#         self._log_unknown_skills(description)

#     def _save_skills(self, db, job, skills: list[tuple[str, str]]):
#         seen_names: set[str] = set()
#         seen_ids:   set[int] = set()

#         for raw_name, skill_type in skills:
#             if not raw_name.strip():
#                 continue

#             # ── กรองผ่าน normalize ก่อนเสมอ ──────────────────────────────
#             canonical = normalize(raw_name)
#             if canonical is None:
#                 # blocked หรือ unknown → ไม่เก็บเลย
#                 continue

#             if canonical in seen_names:
#                 continue
#             seen_names.add(canonical)

#             try:
#                 skill = self.skill_service.get_or_create_skill(db, raw_name, skill_type)
#             except Exception as e:
#                 print(f"  [SKILL ERROR] '{raw_name}': {e}")
#                 db.rollback()
#                 continue

#             if skill is None:
#                 continue

#             if skill.id in seen_ids:
#                 continue
#             seen_ids.add(skill.id)

#             try:
#                 self.job_skill_svc.attach_skill_with_auto_score(db, job, skill)
#             except Exception as e:
#                 print(f"  [SAVE ERROR] '{skill.name}': {e}")
#                 db.rollback()

#     def _extract_from_db(self, db, description: str) -> list[tuple[str, str]]:
#         words      = description.lower().split()
#         conditions = [Skill.name.ilike(f"%{w}%") for w in words[:50]]
#         if not conditions:
#             return []
#         skills = db.query(Skill).filter(or_(*conditions)).all()
#         return [(s.name, s.skill_type) for s in skills]

#     def _extract_simple(self, description: str) -> list[tuple[str, str]]:
#         from app.utils.skill_dict import get_skill_dict, get_synonyms
#         skill_dict = get_skill_dict()
#         synonyms   = get_synonyms()
#         found      = []
#         desc_lower = description.lower()

#         def has_word(word: str) -> bool:
#             return bool(re.search(r'\b' + re.escape(word.lower()) + r'\b', desc_lower))

#         for name, stype in skill_dict.items():
#             if has_word(name):
#                 found.append((name, stype))
#         for alias, real in synonyms.items():
#             if has_word(alias) and real in skill_dict:
#                 found.append((real, skill_dict[real]))
#         return list(set(found))

#     def _log_unknown_skills(self, description: str):
#         try:
#             from app.utils.skill_extractor_unknown import extract_skills
#             _, unknown = extract_skills(description)
#             if unknown:
#                 print(f"  [UNKNOWN] {unknown[:5]}")
#         except Exception:
#             pass

#     # ── Utilities ─────────────────────────────────────────────────────────────

#     def extract_job_id(self, url: str) -> str | None:
#         clean = url.split("#")[0].split("?")[0]
#         m = re.search(r"/job/(\d+)", clean)
#         return m.group(1) if m else None

#     def parse_posted_date(self, text: str):
#         if not text:
#             return datetime.today().date()
#         text = text.lower().strip()
#         today = datetime.today().date()
#         m = re.search(r"(\d+)", text)
#         if not m:
#             return today
#         n = int(m.group(1))
#         if any(u in text for u in ["hour", "ชม.", "minute", "นาที"]):
#             return today
#         if any(u in text for u in ["day", "วัน"]):
#             return today - timedelta(days=n)
#         if any(u in text for u in ["month", "เดือน"]):
#             return today - timedelta(days=n * 30)
#         return today

# app/scraping/job_scraper_service.py  (v2 — structured skill extraction)
# แทน job_scraper_service.py เดิม

from datetime import datetime, timedelta
import re

from sqlalchemy import or_
from app.core.database import SessionLocal
from app.models.skill import Skill
from app.utils.category_config import SUB_CATEGORY_NAMES
from app.ai.ai_service import AIService
from app.ai.ai_skill_extractor import AISkillExtractor   # ← ใหม่
from app.jobs.job_skill_service import JobSkillService
from app.jobs.jobs_repository import JobRepository
from app.scraping.scraper_service import ScraperService
from app.scraping.skill_creator_service import SkillCreatorService


class JobScraperService:

    def __init__(self):
        self.scraper        = ScraperService()
        self.repo           = JobRepository()
        self.skill_service  = SkillCreatorService()
        self.job_skill_svc  = JobSkillService()
        self.ai_service     = AIService()
        self.skill_extractor = AISkillExtractor()   # ← structured extractor

    # ── Main entry point ──────────────────────────────────────────────────────

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
                    print(f"[STOP] No jobs on page {page}")
                    break

                for job in jobs:
                    if inserted >= max_jobs:
                        break

                    external_id = self.extract_job_id(job["detail_url"])
                    if not external_id:
                        continue

                    existing = self.repo.get_by_external_id(db, external_id)
                    if existing:
                        did_update = self._update_if_needed(db, existing, job)
                        updated += did_update
                        skipped += not did_update
                    else:
                        self._insert_new_job(db, job, external_id)
                        inserted += 1
                        print(f"[PROGRESS] inserted={inserted}/{max_jobs}")

                page += 1

            print(f"\n✅ Done — inserted:{inserted} updated:{updated} skipped:{skipped}")
            return inserted
        finally:
            db.close()

    # ── INSERT ────────────────────────────────────────────────────────────────

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
            "sub_category_id":  metadata.get("sub_category_id") or None,
            "experience_level": metadata["experience_level"],
            "job_type":         job.get("job_type"),
        }

        new_job = self.repo.create(db, job_data)
        db.commit()

        self.process_job_skills(db, new_job, description)
        db.commit()
        print(f"[INSERT] {job['title']} → {metadata['sub_category']}")

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def _update_if_needed(self, db, existing, job: dict) -> bool:
        updates      = {}
        needs_detail = False
        needs_skills = False

        current_cat_nm = existing.sub_category.name if existing.sub_category else None
        current_desc   = getattr(existing, "description", None) or ""

        if not current_cat_nm or current_cat_nm not in SUB_CATEGORY_NAMES:
            needs_detail = True
        if len(current_desc.strip()) < 20:
            needs_detail = True
        if self.job_skill_svc.count_skills_for_job(db, existing.id) == 0:
            needs_skills = True
            needs_detail = True

        if existing.salary_min is None and job.get("salary_min") is not None:
            updates["salary_min"] = job["salary_min"]
            updates["salary_max"] = job.get("salary_max")

        if not needs_detail and not updates:
            return False

        description = current_desc
        if needs_detail:
            try:
                detail = self.scraper.fetch_job_detail(job["detail_url"])
                description = detail["description"] or description
                if len(description.strip()) >= 20:
                    updates["description"] = description
            except Exception as e:
                print(f"[WARN] re-fetch failed: {e}")

        current_cat_nm = existing.sub_category.name if existing.sub_category else None
        if not current_cat_nm or current_cat_nm not in SUB_CATEGORY_NAMES:
            if description:
                meta = self.ai_service.extract_job_metadata(
                    title=job["title"], description=description
                )
                updates["sub_category_id"]  = meta.get("sub_category_id") or None
                updates["experience_level"] = meta["experience_level"]

        if updates:
            self.repo.update(db, existing.id, updates)
            db.commit()

        if needs_skills and description:
            self.process_job_skills(db, existing, description)
            db.commit()

        return bool(updates) or needs_skills

    # ── Skills processing — STRUCTURED ────────────────────────────────────────

    def process_job_skills(self, db, job, description: str):
        """
        ใช้ AISkillExtractor ที่ return structured list พร้อม importance_score จริง
        fallback → rule-based canonical matching
        """
        # ── Structured AI extraction ──────────────────────────────────────────
        extracted = self.skill_extractor.extract_skills_structured(
            title=job.title,
            description=description,
        )

        if not extracted:
            print(f"  [WARN] no skills extracted for '{job.title}'")
            return

        seen_skill_ids: set[int] = set()

        for item in extracted:
            raw_name        = item["skill_name"]      # already canonical
            skill_type      = item["skill_type"]
            importance_score = item["importance_score"]

            # SkillCreatorService ทำ normalize + get_or_create
            try:
                skill = self.skill_service.get_or_create_skill(db, raw_name, skill_type)
            except Exception as e:
                print(f"  [SKILL ERROR] '{raw_name}': {e}")
                db.rollback()
                continue

            if skill is None or skill.id in seen_skill_ids:
                continue

            seen_skill_ids.add(skill.id)

            # attach พร้อม importance_score ที่คำนวณจาก tier จริง
            try:
                self.job_skill_svc.attach_skill_with_score(
                    db, job, skill, importance_score
                )
            except Exception as e:
                print(f"  [SAVE ERROR] '{skill.name}': {e}")
                db.rollback()

    # ── Utilities ─────────────────────────────────────────────────────────────

    def extract_job_id(self, url: str) -> str | None:
        clean = url.split("#")[0].split("?")[0]
        m = re.search(r"/job/(\d+)", clean)
        return m.group(1) if m else None

    def parse_posted_date(self, text: str):
        if not text:
            return datetime.today().date()
        text = text.lower().strip()
        today = datetime.today().date()
        m = re.search(r"(\d+)", text)
        if not m:
            return today
        n = int(m.group(1))
        if any(u in text for u in ["hour", "ชม.", "minute", "นาที"]):
            return today
        if any(u in text for u in ["day", "วัน"]):
            return today - timedelta(days=n)
        if any(u in text for u in ["month", "เดือน"]):
            return today - timedelta(days=n * 30)
        return today