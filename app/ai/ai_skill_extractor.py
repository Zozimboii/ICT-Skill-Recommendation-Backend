# app/ai/ai_skill_extractor.py
"""
Structured Skill Extraction — Production Grade

แทน extract_skills เดิมที่ใช้ prompt ง่ายๆ
ด้วย structured extraction ที่:
1. แยก Required / Preferred / Nice-to-have
2. normalize ทุก skill ผ่าน canonical_skills ก่อน save
3. assign importance_score ตาม section จริง (ไม่ใช่ mention_count=1)
4. จำกัดจำนวน skill per job ให้สมเหตุสมผล
"""

import json
import re
import os
import time
from typing import Literal

import google.generativeai as genai
import google.api_core.exceptions

from app.utils.skill_normalizer import normalize, CANONICAL_SKILLS

# ── Importance scores ──────────────────────────────────────────────────────────
SCORE_REQUIRED   = 4.0   # ปรากฏใน Required / Must Have section
SCORE_PREFERRED  = 2.0   # ปรากฏใน Preferred / Good to Have
SCORE_MENTIONED  = 0.8   # mention ในบริบทเฉยๆ

MAX_SKILLS_PER_JOB = 30  # cap ป้องกัน noise


class AISkillExtractor:

    RETRY_WAIT = 30

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

    def _call_ai(self, prompt: str, retries: int = 2) -> str | None:
        for attempt in range(retries + 1):
            try:
                resp = self.model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.0},
                )
                return resp.text
            except google.api_core.exceptions.ResourceExhausted as e:
                m = re.search(r'retry_delay \{\s*seconds: (\d+)', str(e))
                wait = int(m.group(1)) + 2 if m else self.RETRY_WAIT
                if attempt < retries:
                    print(f"[AI QUOTA] 429 — รอ {wait}s ({attempt+1}/{retries})")
                    time.sleep(wait)
                else:
                    print("[AI QUOTA] หมด — ใช้ fallback")
                    return None
            except Exception as e:
                print(f"[AI ERROR] {type(e).__name__}: {e}")
                return None

    def extract_skills_structured(
        self,
        title: str,
        description: str,
    ) -> list[dict]:
        """
        Return list of:
        {
            "skill_name": str,       # canonical name
            "skill_type": str,       # "hard_skill" | "soft_skill"
            "importance_score": float # 4.0 / 2.0 / 0.8
        }

        ไม่เกิน MAX_SKILLS_PER_JOB ตัว
        """
        # ตัด description ให้สั้นลง — ส่วนแรกคือ requirements หลัก
        clean = re.sub(r'\s+', ' ', description).strip()[:4000]

        prompt = f"""You are an expert HR skill extractor. Extract ONLY skills from this job posting.

JOB TITLE: {title}

RULES:
1. Extract skills ONLY from these canonical skill names (use exact spelling):
   Hard Skills: {', '.join(list(CANONICAL_SKILLS.keys())[:80])}
   (more exist — match the closest canonical name)

2. Categorize each skill into ONE of these tiers:
   - "required": appears in "Required", "Must Have", "Qualifications", or is clearly mandatory
   - "preferred": appears in "Preferred", "Nice to Have", "Advantage", "Plus"
   - "mentioned": mentioned in job context but not explicitly required

3. Limit: return maximum 25 skills total (prioritize required > preferred > mentioned)
4. Ignore: certifications, languages (English/Thai), company-specific tools, education requirements

Return ONLY valid JSON. No explanation. No markdown.

SCHEMA:
{{
  "required":  ["skill1", "skill2"],
  "preferred": ["skill3"],
  "mentioned": ["skill4"]
}}

JOB DESCRIPTION:
{clean}"""

        raw = self._call_ai(prompt)

        if raw is None:
            return self._fallback_extract(title, description)

        try:
            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

            parsed = json.loads(raw)

            result = []
            seen:  set[str] = set()
            count  = 0

            tier_score = {
                "required":  SCORE_REQUIRED,
                "preferred": SCORE_PREFERRED,
                "mentioned": SCORE_MENTIONED,
            }

            # เรียงลำดับ: required ก่อน
            for tier in ["required", "preferred", "mentioned"]:
                for raw_name in parsed.get(tier, []):
                    if count >= MAX_SKILLS_PER_JOB:
                        break

                    canonical = normalize(raw_name)
                    if canonical is None or canonical in seen:
                        continue

                    skill_type = CANONICAL_SKILLS.get(canonical, "hard_skill")
                    seen.add(canonical)
                    count += 1

                    result.append({
                        "skill_name":       canonical,
                        "skill_type":       skill_type,
                        "importance_score": tier_score[tier],
                    })

            print(f"[SKILL EXTRACT] '{title}' → {len(result)} skills "
                  f"(req={len(parsed.get('required',[]))}, "
                  f"pref={len(parsed.get('preferred',[]))}, "
                  f"ment={len(parsed.get('mentioned',[]))})")
            return result

        except (json.JSONDecodeError, Exception) as e:
            print(f"[SKILL EXTRACT] parse error: {e} — fallback")
            return self._fallback_extract(title, description)

    def _fallback_extract(self, title: str, description: str) -> list[dict]:
        """
        Rule-based fallback เมื่อ AI ไม่พร้อม
        ใช้ word boundary matching กับ CANONICAL_SKILLS
        assign score ตาม section header ที่พบ
        """
        desc_lower = description.lower()
        result = []
        seen:  set[str] = set()

        # หา section headers เพื่อ assign score
        required_section  = self._find_section(desc_lower, [
            "required", "must have", "qualifications", "requirements", "คุณสมบัติ"
        ])
        preferred_section = self._find_section(desc_lower, [
            "preferred", "nice to have", "advantage", "plus", "ข้อได้เปรียบ"
        ])

        for canonical, skill_type in CANONICAL_SKILLS.items():
            pattern = r'\b' + re.escape(canonical.lower()) + r'\b'
            if not re.search(pattern, desc_lower):
                continue

            canonical_norm = normalize(canonical)
            if canonical_norm is None or canonical_norm in seen:
                continue

            # หา position ที่ match
            match = re.search(pattern, desc_lower)
            pos = match.start() if match else 0

            # assign score ตาม section
            if required_section and required_section[0] <= pos <= required_section[1]:
                score = SCORE_REQUIRED
            elif preferred_section and preferred_section[0] <= pos <= preferred_section[1]:
                score = SCORE_PREFERRED
            else:
                score = SCORE_MENTIONED

            seen.add(canonical_norm)
            result.append({
                "skill_name":       canonical_norm,
                "skill_type":       skill_type,
                "importance_score": score,
            })

            if len(result) >= MAX_SKILLS_PER_JOB:
                break

        # เรียง required ก่อน
        result.sort(key=lambda x: -x["importance_score"])
        print(f"[FALLBACK EXTRACT] '{title}' → {len(result)} skills")
        return result

    def _find_section(
        self,
        text: str,
        keywords: list[str],
    ) -> tuple[int, int] | None:
        """หา start-end index ของ section ที่มี keyword"""
        for kw in keywords:
            idx = text.find(kw)
            if idx >= 0:
                # section จบที่ newline คู่ หรือ 500 chars
                end = text.find("\n\n", idx)
                if end < 0:
                    end = min(idx + 500, len(text))
                return (idx, end)
        return None