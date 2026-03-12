# # app/services/ai_service.py

import hashlib
import os
import re
import google.generativeai as genai
import json
import google.api_core.exceptions 
from app.utils.category_config import KEYWORD_CATEGORY_MAP, SUB_CATEGORY_NAME_TO_ID, SUB_CATEGORY_NAMES

class AIService:

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
        self.MAX_AI_JOBS = 300
        self.ai_counter = 0
        self._cache: dict = {}

    def can_call_ai(self):
        return self.ai_counter < self.MAX_AI_JOBS

    def extract_job_metadata(self, title: str, description: str = "") -> dict:
        normalized = title.strip().lower()
        cache_key = hashlib.md5(normalized.encode()).hexdigest()

        # 1. Cache
        if cache_key in self._cache:
            print(f"[CACHE HIT] {title}")
            return self._cache[cache_key]

        exp = self._guess_experience_level(normalized)

        # 2. Keyword match
        cat = self._keyword_match(normalized)
        if cat:
            result = self._build(cat, exp)
            self._cache[cache_key] = result
            print(f"[KEYWORD] {title} => {cat}")
            return result

        # 3. AI
        if self.can_call_ai():
            ai_result = self._ai_classify(title, description)
            if ai_result:
                self.ai_counter += 1
                self._cache[cache_key] = ai_result
                print(f"[AI #{self.ai_counter}] {title} => {ai_result['sub_category']}")
                return ai_result

        # 4. Fallback
        result = self._build("Developers/Programmers", exp)
        self._cache[cache_key] = result
        print(f"[FALLBACK] {title} => Developers/Programmers")
        return result
    def extract_skills(self, description: str) -> dict:
        try:
            prompt = f"""
                 ## Instruction
                 You are a professional IT recruiter. Extract skills from the job description.

                 ## Context
                 - hard_skills: technical tools, languages, frameworks, platforms
                 - soft_skills: interpersonal / behavioral traits

                 ## Output
                 Return ONLY valid JSON. No markdown. No explanation.
                 {{
                   "hard_skills": ["Python", "SQL"],
                   "soft_skills": ["Communication"]
                 }}

                 ## Job Description
                 {description[:3000]}
        """
            resp = self.model.generate_content(prompt, generation_config={"temperature": 0.1})
            text = resp.text.strip().replace("```json","").replace("```","")
            return json.loads(text)
        except google.api_core.exceptions.ResourceExhausted:
            print(f"[AI QUOTA] extract_skills — rate limit reached, using fallback")
            return {"hard_skills": [], "soft_skills": []}
        except Exception as e:
            print(f"[AI ERROR] extract_skills: {e}")
            return {"hard_skills": [], "soft_skills": []}
        
    def _keyword_match(self, title_lower: str) -> str | None:
        for keyword, category in KEYWORD_CATEGORY_MAP:
            if keyword in title_lower:
                return category
        return None
    
    def _ai_classify(self, title: str, description: str) -> dict | None:
        category_list = "\n".join(f"  - {n}" for n in SUB_CATEGORY_NAMES)
        desc_snippet = description[:500].strip() or "N/A"
        prompt = f"""
## Instruction
Classify the IT job posting into the correct sub-category.

## Context
Thai IT job board (JobsDB Thailand).
Choose EXACTLY from the approved list. Do NOT invent categories.

## Approved Sub-Categories
{category_list}

## Input
Job Title: {title}
Job Description (excerpt): {desc_snippet}

## Output
Return ONLY valid JSON. No markdown. No explanation.
{{
  "sub_category": "<exact name from approved list>",
  "experience_level": "<junior | mid | senior | any>"
}}

Rules:
- senior → Senior, Sr., Lead, Principal, Head
- junior → Junior, Jr., Entry, Graduate
- mid    → Mid, Middle
- any    → otherwise
"""
        try:
            resp = self.model.generate_content(prompt, generation_config={"temperature": 0.0})
            text = resp.text.strip().replace("```json","").replace("```","")
            data = json.loads(text)
            sub_cat = data.get("sub_category","").strip()
            exp     = data.get("experience_level","any").strip()
            if sub_cat not in SUB_CATEGORY_NAME_TO_ID:
                print(f"[AI WARN] '{sub_cat}' not in approved list, fallback")
                sub_cat = "Developers/Programmers"
            return self._build(sub_cat, exp)
        except google.api_core.exceptions.ResourceExhausted:
            print(f"[AI QUOTA] _ai_classify '{title}' — rate limit, using keyword/fallback")
            return None
        except Exception as e:
            print(f"[AI ERROR] _ai_classify: {type(e).__name__}")
            return None

    def _build(self, sub_category: str, experience_level: str) -> dict:
        return {
            "sub_category":     sub_category,
            "sub_category_id":  SUB_CATEGORY_NAME_TO_ID.get(sub_category, 0),
            "experience_level": experience_level,
        }

    def _guess_experience_level(self, t: str) -> str:
        if any(k in t for k in ["senior","sr.","lead","principal","head of"]):
            return "senior"
        if any(k in t for k in ["junior","jr.","entry","graduate"]):
            return "junior"
        if any(k in t for k in ["mid-level","mid level","middle"]):
            return "mid"
        return "any"