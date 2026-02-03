# app/services/ai_service.py
import os
from typing import Dict, Optional

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def _has_provider_key(provider: str) -> bool:
    if provider == "gemini":
        return bool(GEMINI_API_KEY)
    return bool(OPENAI_API_KEY)


def format_database_answer(db_data: Dict) -> str:
    parts = []

    if db_data.get("skill_name"):
        skill_name = db_data["skill_name"]
        job_count = db_data.get("job_count", 0)
        skill_type = db_data.get("skill_type", "")

        parts.append(f"**{skill_name}**")
        if skill_type:
            parts.append(f"ประเภท: {skill_type}")
        parts.append(f"พบในงานทั้งหมด: {job_count:,} ตำแหน่ง")

    if db_data.get("top_subcategories"):
        parts.append("\n**สายงานที่ใช้ทักษะนี้:**")
        for cat in db_data["top_subcategories"][:5]:
            parts.append(f"- {cat['sub_category_name']} ({cat['count']} ตำแหน่ง)")

    if db_data.get("related_skills"):
        parts.append("\n**ทักษะที่เกี่ยวข้อง (มักใช้ร่วมกัน):**")
        for s in db_data["related_skills"][:10]:
            parts.append(f"- {s['skill_name']} ({s['count']} ตำแหน่ง)")

    return "\n".join(parts)


def _summarize_with_openai(question: str, db_answer: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = (
        "คุณเป็นผู้ช่วยด้านทักษะและอาชีพในสาย ICT "
        "ช่วยสรุปข้อมูลจากฐานข้อมูล และแนะนำแนวทางต่อยอดให้เข้าใจง่าย"
    )

    user_message = f"""คำถาม: {question}

ข้อมูลจากฐานข้อมูล:
{db_answer}

สรุป + แนะนำต่อยอดให้กระชับ ชัดเจน (ภาษาไทย)
"""

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


def _summarize_with_gemini(question: str, db_answer: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""คุณเป็นผู้ช่วยด้านทักษะและอาชีพในสาย ICT
คำถาม: {question}

ข้อมูลจากฐานข้อมูล:
{db_answer}

สรุป + แนะนำต่อยอดให้กระชับ ชัดเจน (ภาษาไทย)
"""
    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    return (getattr(resp, "text", "") or "").strip()


def get_fallback_response(question: str) -> str:
    q = question.lower()
    if any(x in q for x in ["python", "ไพธอน"]):
        return "Python นิยมมากใน ICT ใช้ได้ทั้ง Data, Web, AI แนะนำเริ่มจากพื้นฐาน syntax แล้วทำโปรเจกต์เล็ก ๆ ครับ"
    if any(x in q for x in ["data", "ข้อมูล", "analyst"]):
        return (
            "สาย Data Analyst แนะนำ SQL + Excel/Power BI และ Python สำหรับวิเคราะห์ข้อมูลครับ"
        )
    return "ยังไม่ได้ตั้งค่า AI key ตอนนี้เลยตอบแบบพื้นฐานได้ ลองถามให้เจาะจงสกิล/สายงานมากขึ้นได้นะครับ"


def get_ai_response(
    question: str, db_data: Optional[Dict] = None, use_ai: bool = True
) -> str:
    # 1) ถ้ามี db_data ให้ตอบจาก db ก่อน
    if db_data and db_data.get("skill_name"):
        db_answer = format_database_answer(db_data)

        if (not use_ai) or (not _has_provider_key(AI_PROVIDER)):
            return db_answer

        try:
            if AI_PROVIDER == "gemini":
                ai_summary = _summarize_with_gemini(question, db_answer)
            else:
                ai_summary = _summarize_with_openai(question, db_answer)

            return f"{ai_summary}\n\n---\n\n**ข้อมูลจากฐานข้อมูล:**\n{db_answer}"
        except Exception:
            return db_answer

    # 2) ไม่มี db_data → ใช้ AI หรือ fallback
    if (not use_ai) or (not _has_provider_key(AI_PROVIDER)):
        return get_fallback_response(question)

    try:
        # ถ้าต้องการ general chat ค่อยแยกเพิ่มทีหลังได้
        if AI_PROVIDER == "gemini":
            return _summarize_with_gemini(question, "")
        return _summarize_with_openai(question, "")
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {str(e)}"
