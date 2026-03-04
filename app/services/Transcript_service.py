import json
import os
from typing import Dict, List, Optional
from io import BytesIO

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.db.models import Job_transcript, User

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF file bytes.
    """
    reader = PdfReader(BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text.strip()

def extract_text(file_bytes: bytes, file_ext: str) -> str:
    """
    Extract text depending on file extension.
    """
    if file_ext == ".pdf":
        return extract_text_from_pdf(file_bytes)

    elif file_ext == ".txt":
        return file_bytes.decode("utf-8")

    else:
        return file_bytes.decode("utf-8", errors="ignore")
    
def extract_skills_from_transcript(transcript_text: str) -> Dict[str, List[str]]:
    """
    Use Gemini AI to extract hard and soft skills from transcript text.
    """
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        return {"hard_skills": [], "soft_skills": [], "recommend_job": []}

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""
คุณเป็นผู้เชี่ยวชาญด้านการประเมินทักษะในสาย ICT

จากข้อความต่อไปนี้:
{transcript_text}

กรุณาแยก Hard Skills และ Soft Skills
และแนะนำสายงานที่เหมาะสมที่สุดสำหรับผู้ที่มีทักษะเหล่านี้ อย่างน้อย 5 สายงาน
ตอบเฉพาะ JSON ในรูปแบบนี้เท่านั้น:
{{
  "hard_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "recommend_job": ["job1", "job2", "job3"]
}}
"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        response_text = (getattr(response, "text", "") or "").strip()

        # Remove markdown block if exists
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            response_text = response_text.replace("json", "").strip()

        result = json.loads(response_text)

        return {
            "hard_skills": result.get("hard_skills", []),
            "soft_skills": result.get("soft_skills", []),
            "recommend_job": result.get("recommend_job", [])
        }

    except Exception:
        return {"hard_skills": [], "soft_skills": [], "recommend_job": []}

def save_transcript_skills(
    db: Session,
    username: str,
    file_name: str,
    hard_skills: List[str],
    soft_skills: List[str],
    recommend_job: List[str]
) -> Dict:

    transcript = Job_transcript(
        username=username,
        file_name=file_name,
        hard_skills=", ".join(hard_skills),
        soft_skills=", ".join(soft_skills),
        recommend_job=", ".join(recommend_job)
    )

    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    return {
        "id": transcript.id,
        "username": transcript.username,
        "file_name": transcript.file_name,
        "hard_skills": hard_skills,
        "soft_skills": soft_skills,
        "recommend_job": recommend_job
    }

def process_transcript_file(
    db: Session,
    username: str,
    file_name: str,
    file_bytes: bytes,
    file_ext: str
) -> Dict:
    """
    Main processing flow:
    1. Extract text
    2. Extract skills via AI
    3. Save to DB
    """

    text_content = extract_text(file_bytes, file_ext)

    if not text_content.strip():
        return {
            "id": None,
            "username": username,
            "file_name": None,
            "hard_skills": [],
            "soft_skills": [],
            "recommend_job": []
        }

    skills = extract_skills_from_transcript(text_content)

    return save_transcript_skills(
    db=db,
    username=username,
    file_name=file_name,
    hard_skills=skills["hard_skills"],
    soft_skills=skills["soft_skills"],
    recommend_job=skills["recommend_job"]
)


def get_transcript_by_id(db: Session, transcript_id: int) -> Optional[Dict]:

    transcript = db.query(Job_transcript).filter(
        Job_transcript.id == transcript_id
    ).first()

    if not transcript:
        return None

    hard_skills = (
        [s.strip() for s in transcript.hard_skills.split(",")]
        if transcript.hard_skills else []
    )

    soft_skills = (
        [s.strip() for s in transcript.soft_skill.split(",")]
        if transcript.soft_skill else []
    )

    recommend_job = (
        [s.strip() for s in transcript.recommend_job.split(",")]
        if transcript.recommend_job else []
    )

    return {
        "id": transcript.id,
        "username": transcript.username,
        "file_name": transcript.file_name,
        "hard_skills": hard_skills,
        "soft_skills": soft_skills,
        "recommend_job": recommend_job
    }

def get_all_transcripts(db: Session) -> List[Dict]:

    transcripts = db.query(Job_transcript).all()
    result = []

    for transcript in transcripts:

        hard_skills = (
            [s.strip() for s in transcript.hard_skills.split(",")]
            if transcript.hard_skills else []
        )

        soft_skills = (
            [s.strip() for s in transcript.soft_skills.split(",")]
            if transcript.soft_skills else []
        )

        recommend_job = (
            [s.strip() for s in transcript.recommend_job.split(",")]
            if transcript.recommend_job else []
        )

        result.append({
            "id": transcript.id,
            "username": transcript.username,
            "file_name": transcript.file_name,
            "hard_skills": hard_skills,
            "soft_skills": soft_skills,
            "recommend_job": recommend_job
        })

    return result