# app/services/job_scraper_service_patch.py
# """
# แก้เฉพาะส่วน _save_unique_skills ใน JobScraperService
# copy ไปแทนใน job_scraper_service.py
# """

# def _save_unique_skills(self, db, job, skills: list):
#     seen_names:     set[str] = set()
#     seen_skill_ids: set[int] = set()

#     for skill_name, skill_type, *_rest in skills:
#         raw = skill_name.strip()
#         if not raw:
#             continue

#         # normalize ก่อน check duplicate เพื่อ prevent "aws" + "Amazon Web Services" นับ 2
#         from app.utils.skill_normalizer import normalize
#         canonical = normalize(raw)
#         if canonical is None:
#             continue  # blocked หรือ unknown

#         if canonical in seen_names:
#             continue
#         seen_names.add(canonical)

#         try:
#             skill = self.skill_service.get_or_create_skill(db, raw, skill_type)
#         except Exception as e:
#             print(f"  [SKILL ERROR] '{raw}': {e}")
#             db.rollback()
#             continue

#         if skill is None:
#             continue  # blocked

#         if skill.id in seen_skill_ids:
#             continue
#         seen_skill_ids.add(skill.id)

#         try:
#             self.job_skill_service.attach_skill_with_auto_score(db, job, skill)
#         except Exception as e:
#             print(f"  [SAVE ERROR] '{skill.name}': {e}")
#             db.rollback()