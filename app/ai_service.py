"""
AI Service สำหรับถามตอบเกี่ยวกับทักษะและอาชีพ ICT
"""
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

# ตรวจสอบว่ามี OpenAI API key หรือไม่
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# à¹€à¸¥à¸·à¸­à¸ provider: openai | gemini
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

# Gemini API key / model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

def format_database_answer(db_data: Dict) -> str:
    """
    จัดรูปแบบคำตอบจากข้อมูล database เป็นข้อความที่อ่านง่าย
    
    Args:
        db_data: ข้อมูลจาก database
    
    Returns:
        ข้อความที่จัดรูปแบบแล้ว
    """
    answer_parts = []
    
    # ข้อมูล skill หลัก
    if db_data.get("skill_name"):
        skill_name = db_data["skill_name"]
        job_count = db_data.get("job_count", 0)
        skill_type = db_data.get("skill_type", "")
        
        answer_parts.append(f"**{skill_name}**")
        if skill_type:
            answer_parts.append(f"ประเภท: {skill_type}")
        answer_parts.append(f"พบในงานทั้งหมด: {job_count:,} ตำแหน่ง")
    
    # Top categories ที่ใช้ skill นี้
    if db_data.get("top_subcategories"):
        answer_parts.append("\n**สายงานที่ใช้ทักษะนี้:**")
        for cat in db_data["top_subcategories"][:5]:  # แสดงแค่ 5 อันแรก
            answer_parts.append(f"- {cat['sub_category_name']} ({cat['count']} ตำแหน่ง)")
    
    # Related skills
    if db_data.get("related_skills"):
        answer_parts.append("\n**ทักษะที่เกี่ยวข้อง (มักใช้ร่วมกัน):**")
        for skill in db_data["related_skills"][:10]:  # แสดงแค่ 10 อันแรก
            answer_parts.append(f"- {skill['skill_name']} ({skill['count']} ตำแหน่ง)")
    
    return "\n".join(answer_parts)



def _has_provider_key(provider: str) -> bool:
    if provider == "gemini":
        return bool(GEMINI_API_KEY)
    return bool(OPENAI_API_KEY)


def _summarize_with_openai(question: str, db_answer: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = """à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT
à¸„à¸¸à¸“à¹„à¸”à¹‰à¸£à¸±à¸šà¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸ˆà¸²à¸à¸à¸²à¸™à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸ˆà¸³à¸™à¸§à¸™à¸‡à¸²à¸™à¸—à¸µà¹ˆà¸•à¹‰à¸­à¸‡à¸à¸²à¸£à¸—à¸±à¸à¸©à¸°à¸™à¸µà¹‰
à¸Šà¹ˆà¸§à¸¢à¸ªà¸£à¸¸à¸›à¹à¸¥à¸°à¹ƒà¸«à¹‰à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡à¹€à¸›à¹‡à¸™à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¸—à¸µà¹ˆà¹€à¸‚à¹‰à¸²à¹ƒà¸ˆà¸‡à¹ˆà¸²à¸¢à¹à¸¥à¸°à¹€à¸›à¹‡à¸™à¸¡à¸´à¸•à¸£"""

    user_message = f"""à¸„à¸³à¸–à¸²à¸¡: {question}

à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸ˆà¸²à¸à¸à¸²à¸™à¸‚à¹‰à¸­à¸¡à¸¹à¸¥:
{db_answer}

à¸à¸£à¸¸à¸“à¸²à¸ªà¸£à¸¸à¸›à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸‚à¹‰à¸²à¸‡à¸•à¹‰à¸™à¹à¸¥à¸°à¹ƒà¸«à¹‰à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸—à¸±à¸à¸©à¸°à¸™à¸µà¹‰"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def _summarize_with_gemini(question: str, db_answer: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT

à¸„à¸³à¸–à¸²à¸¡: {question}

à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸ˆà¸²à¸à¸à¸²à¸™à¸‚à¹‰à¸­à¸¡à¸¹à¸¥:
{db_answer}

à¸à¸£à¸¸à¸“à¸²à¸ªà¸£à¸¸à¸›à¸‚à¹‰à¸­à¸¡à¸¹à¸¥à¸‚à¹‰à¸²à¸‡à¸•à¹‰à¸™à¹à¸¥à¸°à¹ƒà¸«à¹‰à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸žà¸´à¹ˆà¸¡à¹€à¸•à¸´à¸¡à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸—à¸±à¸à¸©à¸°à¸™à¸µà¹‰ (à¸•à¸­à¸šà¸ à¸²à¸©à¸²à¹„à¸—à¸¢ à¸à¸£à¸°à¸Šà¸±à¸š à¸Šà¸±à¸”à¹€à¸ˆà¸™)"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(prompt)
        
        # ตรวจสอบ response
        if hasattr(resp, 'text') and resp.text:
            return resp.text.strip()
        elif hasattr(resp, 'candidates') and resp.candidates:
            return resp.candidates[0].content.parts[0].text.strip()
        else:
            raise Exception("No response from Gemini")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def _general_chat_with_openai(question: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = """à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT (Information and Communication Technology)
à¸„à¸¸à¸“à¸Šà¹ˆà¸§à¸¢à¸•à¸­à¸šà¸„à¸³à¸–à¸²à¸¡à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸š:
- à¸—à¸±à¸à¸©à¸°à¸—à¸µà¹ˆà¸ˆà¸³à¹€à¸›à¹‡à¸™à¸ªà¸³à¸«à¸£à¸±à¸šà¸­à¸²à¸Šà¸µà¸žà¸•à¹ˆà¸²à¸‡à¹† à¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT
- à¹à¸™à¸°à¸™à¸³à¸—à¸±à¸à¸©à¸°à¸—à¸µà¹ˆà¸„à¸§à¸£à¹€à¸£à¸µà¸¢à¸™à¸£à¸¹à¹‰
- à¹€à¸—à¸£à¸™à¸”à¹Œà¸‚à¸­à¸‡à¸—à¸±à¸à¸©à¸°à¹ƒà¸™à¸•à¸¥à¸²à¸”à¸‡à¸²à¸™
- à¸„à¸³à¹à¸™à¸°à¸™à¸³à¹€à¸à¸µà¹ˆà¸¢à¸§à¸à¸±à¸šà¸à¸²à¸£à¸žà¸±à¸’à¸™à¸²à¸—à¸±à¸à¸©à¸°à¸­à¸²à¸Šà¸µà¸ž

à¸•à¸­à¸šà¹€à¸›à¹‡à¸™à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¸—à¸µà¹ˆà¹€à¸‚à¹‰à¸²à¹ƒà¸ˆà¸‡à¹ˆà¸²à¸¢à¹à¸¥à¸°à¹€à¸›à¹‡à¸™à¸¡à¸´à¸•à¸£"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def _general_chat_with_gemini(question: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""à¸„à¸¸à¸“à¹€à¸›à¹‡à¸™à¸œà¸¹à¹‰à¸Šà¹ˆà¸§à¸¢à¸—à¸µà¹ˆà¹€à¸Šà¸µà¹ˆà¸¢à¸§à¸Šà¸²à¸à¸”à¹‰à¸²à¸™à¸—à¸±à¸à¸©à¸°à¹à¸¥à¸°à¸­à¸²à¸Šà¸µà¸žà¹ƒà¸™à¸ªà¸²à¸‚à¸² ICT
à¸•à¸­à¸šà¸„à¸³à¸–à¸²à¸¡à¹€à¸›à¹‡à¸™à¸ à¸²à¸©à¸²à¹„à¸—à¸¢à¸—à¸µà¹ˆà¹€à¸‚à¹‰à¸²à¹ƒà¸ˆà¸‡à¹ˆà¸²à¸¢à¹à¸¥à¸°à¹€à¸›à¹‡à¸™à¸¡à¸´à¸•à¸£

à¸„à¸³à¸–à¸²à¸¡: {question}"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(prompt)
        
        # ตรวจสอบ response
        if hasattr(resp, 'text') and resp.text:
            return resp.text.strip()
        elif hasattr(resp, 'candidates') and resp.candidates:
            return resp.candidates[0].content.parts[0].text.strip()
        else:
            raise Exception("No response from Gemini")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def get_ai_response(question: str, db_data: Optional[Dict] = None, use_ai: bool = True) -> str:
    """
    รับคำถามและส่งคืนคำตอบ โดยใช้ข้อมูลจาก database เป็นหลัก แล้วใช้ AI ช่วยสรุป
    
    Args:
        question: คำถามจากผู้ใช้
        db_data: ข้อมูลจาก database (skill info, job count, etc.)
        use_ai: ใช้ AI ช่วยสรุปหรือไม่
    
    Returns:
        คำตอบที่รวมข้อมูลจาก database และ AI
    """
    # ถ้ามีข้อมูลจาก database ให้ใช้เป็นคำตอบหลัก
    if db_data and db_data.get("skill_name"):
        db_answer = format_database_answer(db_data)
        
        # ถ้าไม่ต้องการใช้ AI หรือไม่มี API key ให้คืนคำตอบจาก database เท่านั้น
        if not use_ai or not _has_provider_key(AI_PROVIDER):
            return db_answer
        
        # ใช้ AI ช่วยสรุปและเพิ่มเติม
        try:
            if AI_PROVIDER == "gemini":
                ai_summary = _summarize_with_gemini(question, db_answer)
            else:
                ai_summary = _summarize_with_openai(question, db_answer)
            
            return f"{ai_summary}\n\n---\n\n**ข้อมูลจากฐานข้อมูล:**\n{db_answer}"
        
        except ImportError:
            return db_answer
        except Exception as e:
            # ถ้า AI error ให้คืนข้อมูลจาก database
            return db_answer
    
    # ถ้าไม่มีข้อมูลจาก database ให้ใช้ AI หรือ fallback
    if not use_ai or not _has_provider_key(AI_PROVIDER):
        return get_fallback_response(question)
    
    try:
        if AI_PROVIDER == "gemini":
            return _general_chat_with_gemini(question)
        return _general_chat_with_openai(question)
    
    except ImportError:
        return get_fallback_response(question)
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {str(e)}"

def get_fallback_response(question: str) -> str:
    """
    คำตอบสำรองเมื่อไม่มี OpenAI API key หรือเกิดข้อผิดพลาด
    """
    question_lower = question.lower()
    
    # Rule-based responses
    if any(word in question_lower for word in ["python", "ไพธอน"]):
        return "Python เป็นภาษาที่ได้รับความนิยมมากในสาขา ICT ใช้ได้ทั้งในงาน Data Science, Web Development, และ AI/ML. แนะนำให้เริ่มเรียนรู้จากพื้นฐาน syntax แล้วค่อยไปต่อยอดตามสายงานที่สนใจครับ"
    
    elif any(word in question_lower for word in ["web", "เว็บ", "frontend", "backend"]):
        return "สำหรับงาน Web Development แนะนำให้เรียนรู้ HTML, CSS, JavaScript เป็นพื้นฐาน แล้วเลือก framework ตามที่สนใจ เช่น React, Vue, หรือ Nuxt สำหรับ frontend และ Node.js, Python (Django/Flask) สำหรับ backend ครับ"
    
    elif any(word in question_lower for word in ["data", "ข้อมูล", "analyst"]):
        return "สำหรับงาน Data Analyst แนะนำให้เรียนรู้ SQL สำหรับ query ข้อมูล, Python หรือ R สำหรับวิเคราะห์ข้อมูล, และเครื่องมือ visualization เช่น Power BI หรือ Tableau ครับ"
    
    elif any(word in question_lower for word in ["ai", "machine learning", "ml"]):
        return "สำหรับงาน AI/ML แนะนำให้เริ่มจาก Python, Math (Linear Algebra, Statistics), และ library เช่น Pandas, NumPy, Scikit-learn สำหรับ Machine Learning พื้นฐาน แล้วค่อยไปต่อยอด Deep Learning ครับ"
    
    elif any(word in question_lower for word in ["เริ่ม", "เริ่มต้น", "ควรเรียน", "แนะนำ"]):
        return "แนะนำให้เริ่มจากทักษะพื้นฐานที่ใช้ได้หลายสายงาน เช่น Python, SQL, และ Excel แล้วค่อยเลือกสายงานที่สนใจเพื่อพัฒนาทักษะเฉพาะทางต่อไปครับ"
    
    else:
        return "ขอบคุณสำหรับคำถามครับ สำหรับคำแนะนำที่ละเอียดขึ้น กรุณาเพิ่ม OPENAI_API_KEY ในไฟล์ .env เพื่อใช้ AI chatbot แบบเต็มรูปแบบ หรือลองถามเกี่ยวกับทักษะเฉพาะ เช่น Python, Web Development, Data Analysis ครับ"
