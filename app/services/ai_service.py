# # app/services/ai_service.py
# import os
# from typing import Dict, Optional

# from dotenv import load_dotenv

# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


# def _has_provider_key(provider: str) -> bool:
#     if provider == "gemini":
#         return bool(GEMINI_API_KEY)
#     return bool(OPENAI_API_KEY)


# def format_database_answer(db_data: Dict) -> str:
#     parts = []

#     if db_data.get("skill_name"):
#         skill_name = db_data["skill_name"]
#         job_count = db_data.get("job_count", 0)
#         skill_type = db_data.get("skill_type", "")

#         parts.append(f"**{skill_name}**")
#         if skill_type:
#             parts.append(f"ประเภท: {skill_type}")
#         parts.append(f"พบในงานทั้งหมด: {job_count:,} ตำแหน่ง")

#     if db_data.get("top_subcategories"):
#         parts.append("\n**สายงานที่ใช้ทักษะนี้:**")
#         for cat in db_data["top_subcategories"][:5]:
#             parts.append(f"- {cat['sub_category_name']} ({cat['count']} ตำแหน่ง)")

#     if db_data.get("related_skills"):
#         parts.append("\n**ทักษะที่เกี่ยวข้อง (มักใช้ร่วมกัน):**")
#         for s in db_data["related_skills"][:10]:
#             parts.append(f"- {s['skill_name']} ({s['count']} ตำแหน่ง)")

#     return "\n".join(parts)


# def _summarize_with_openai(question: str, db_answer: str) -> str:
#     from openai import OpenAI

#     client = OpenAI(api_key=OPENAI_API_KEY)

#     system_prompt = (
#         "คุณเป็นผู้ช่วยด้านทักษะและอาชีพในสาย ICT "
#         "ช่วยสรุปข้อมูลจากฐานข้อมูล และแนะนำแนวทางต่อยอดให้เข้าใจง่าย"
#     )

#     user_message = f"""คำถาม: {question}

# ข้อมูลจากฐานข้อมูล:
# {db_answer}

# สรุป + แนะนำต่อยอดให้กระชับ ชัดเจน (ภาษาไทย)
# """

#     resp = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message},
#         ],
#         temperature=0.7,
#         max_tokens=500,
#     )
#     return resp.choices[0].message.content.strip()


# def _summarize_with_gemini(question: str, db_answer: str) -> str:
#     import google.generativeai as genai

#     genai.configure(api_key=GEMINI_API_KEY)

#     prompt = f"""คุณเป็นผู้ช่วยด้านทักษะและอาชีพในสาย ICT
# คำถาม: {question}

# ข้อมูลจากฐานข้อมูล:
# {db_answer}

# สรุป + แนะนำต่อยอดให้กระชับ ชัดเจน (ภาษาไทย)
# """
#     model = genai.GenerativeModel(GEMINI_MODEL)
#     resp = model.generate_content(prompt)
#     return (getattr(resp, "text", "") or "").strip()


# def get_fallback_response(question: str) -> str:
#     q = question.lower()
#     if any(x in q for x in ["python", "ไพธอน"]):
#         return "Python นิยมมากใน ICT ใช้ได้ทั้ง Data, Web, AI แนะนำเริ่มจากพื้นฐาน syntax แล้วทำโปรเจกต์เล็ก ๆ ครับ"
#     if any(x in q for x in ["data", "ข้อมูล", "analyst"]):
#         return (
#             "สาย Data Analyst แนะนำ SQL + Excel/Power BI และ Python สำหรับวิเคราะห์ข้อมูลครับ"
#         )
#     return "ยังไม่ได้ตั้งค่า AI key ตอนนี้เลยตอบแบบพื้นฐานได้ ลองถามให้เจาะจงสกิล/สายงานมากขึ้นได้นะครับ"


# def get_ai_response(
#     question: str, db_data: Optional[Dict] = None, use_ai: bool = True
# ) -> str:
#     # 1) ถ้ามี db_data ให้ตอบจาก db ก่อน
#     if db_data and db_data.get("skill_name"):
#         db_answer = format_database_answer(db_data)

#         if (not use_ai) or (not _has_provider_key(AI_PROVIDER)):
#             return db_answer

#         try:
#             if AI_PROVIDER == "gemini":
#                 ai_summary = _summarize_with_gemini(question, db_answer)
#             else:
#                 ai_summary = _summarize_with_openai(question, db_answer)

#             return f"{ai_summary}\n\n---\n\n**ข้อมูลจากฐานข้อมูล:**\n{db_answer}"
#         except Exception:
#             return db_answer

#     # 2) ไม่มี db_data → ใช้ AI หรือ fallback
#     if (not use_ai) or (not _has_provider_key(AI_PROVIDER)):
#         return get_fallback_response(question)

#     try:
#         # ถ้าต้องการ general chat ค่อยแยกเพิ่มทีหลังได้
#         if AI_PROVIDER == "gemini":
#             return _summarize_with_gemini(question, "")
#         return _summarize_with_openai(question, "")
#     except Exception as e:
#         return f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {str(e)}"


# import os
# import re
# import google.generativeai as genai
# import json

# class AIService:

#     def __init__(self):
#         genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#         self.model = genai.GenerativeModel(
#             os.getenv("GEMINI_MODEL")
#         )
#         self.MAX_AI_JOBS = 100
#         self.ai_counter = 0

#     def can_call_ai(self):
#         return self.ai_counter < self.MAX_AI_JOBS
    
#     def extract_skills(self, description: str):

#         try:
#             description = description[:3000]

#             prompt = f"""
#                 Act as a professional recruiter. Extract technical skills (hard_skills) and interpersonal skills (soft_skills) from the provided job descriptions.
    
#                 IMPORTANT: Return ONLY a valid JSON list of objects. No preamble, no explanation, no markdown blocks.

#                 Return JSON only:
#                 {{
#                   "hard_skills": [],
#                   "soft_skills": []
#                 }}

#                 Job Description:
#                 {description}
#                 """

#             response = self.model.generate_content(
#                 prompt,
#                 generation_config={"temperature": 0.2}
#             )

#             text = response.text.strip()
#             text = text.replace("```json", "").replace("```", "")
#             return json.loads(text)

#         except Exception as e:
#             print("AI ERROR:", e)
#             return {
#                 "hard_skills": [],
#                 "soft_skills": []
#             }
        
#     import json

#     def extract_batch_skills(self, descriptions: list):

#         # descriptions_json = json.dumps(descriptions, ensure_ascii=False)

#         prompt = f"""
#         You are a strict JSON generator.

#         Act as a professional recruiter. Extract technical skills (hard_skills) and interpersonal skills (soft_skills) from the provided job descriptions.
    
#         IMPORTANT: Return ONLY a valid JSON list of objects. No preamble, no explanation, no markdown blocks.

#         FORMAT:
#         [
#           {{
#             "hard_skills": ["Skill1", "Skill2"],
#             "soft_skills": ["SkillA", "SkillB"]
#           }}
#         ]
        
#         Job Descriptions:
#         {json.dumps(descriptions, ensure_ascii=False)} 
#         """

#         response = self.model.generate_content(
#             prompt,
#             generation_config={
#                 "temperature": 0.1, # ลดความสร้างสรรค์ลงเพื่อให้โครงสร้างคงที่
#                 "response_mime_type": "application/json" # บังคับ Output เป็น JSON
#             }
#         )

#         text = response.text.strip()
#         json_match = re.search(r'\[.*\]', text, re.DOTALL)
#         if json_match:
#             clean_text = json_match.group()
#         else:
#             clean_text = text

#         try:
#             return json.loads(clean_text)
#         except json.JSONDecodeError as e:
#             print(f"❌ JSON Error at: {clean_text[:100]}") # พิมพ์ดูว่ามันพังตรงไหน
#             # หากพัง อาจจะลอง return list ว่าง เพื่อไม่ให้ระบบหยุดทำงาน (Stop-gap)
#             return [{"hard_skills": [], "soft_skills": []} for _ in descriptions]
#         # return json.loads(text)

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