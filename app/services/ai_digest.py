# app/services/ai_digest.py
import os
import json
from typing import Dict, Optional, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def extract_skills_from_job(title: str, description: str) -> Dict[str, List[str]]:
    """
    ใช้ Gemini 2.5 Flash เพื่อแยก hard_skill และ soft_skill จาก job title และ description
    
    Args:
        title: Job title
        description: Job description
        
    Returns:
        Dict with 'hard_skills' and 'soft_skills' lists
    """
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not found, returning empty skills")
        return {"hard_skills": [], "soft_skills": []}
    
    try:
        prompt = f"""
        จากตำแหน่งงานต่อไปนี้ โปรดแยกทักษะออกเป็นสองประเภท:
        
        **ตำแหน่ง:** {title}
        
        **รายละเอียดงาน:**
        {description}
        
        ==================================================
        
        โปรดแยก skills ออกเป็น:
        1. **Hard Skills** (ทักษะเชิงเทคนิค) เช่น: Python, SQL, JavaScript, AWS, Docker, React ฯลฯ
        2. **Soft Skills** (ทักษะนุ่ม) เช่น: Communication, Leadership, Problem Solving, Teamwork ฯลฯ
        
        ให้ return ผลลัพธ์เป็น JSON format เท่านั้น (ไม่มีข้อความอื่น) ดังนี้:
        {{
            "hard_skills": ["skill1", "skill2", "skill3"],
            "soft_skills": ["skill1", "skill2", "skill3"]
        }}
        """
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Parse JSON from response
        response_text = response.text.strip()
        
        # ลองหา JSON object ใน response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            
            # Validate structure
            if "hard_skills" in result and "soft_skills" in result:
                return {
                    "hard_skills": result.get("hard_skills", []),
                    "soft_skills": result.get("soft_skills", [])
                }
        
        print(f"⚠️ Failed to parse JSON response: {response_text}")
        return {"hard_skills": [], "soft_skills": []}
        
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return {"hard_skills": [], "soft_skills": []}


def process_job_skills_batch(jobs_data: List[Dict]) -> List[Dict]:
    """
    Process a batch of jobs and extract skills for each
    
    Args:
        jobs_data: List of job records with id, title, description
        
    Returns:
        List of skill records to be inserted into job_skills_withdes table
    """
    skill_records = []
    
    for idx, job in enumerate(jobs_data):
        print(f"[{idx+1}/{len(jobs_data)}] Processing: {job.get('title', '')[:50]}...")
        
        job_id = job.get('id')
        title = job.get('title', '')
        description = job.get('description', '')
        
        if not title:
            continue
        
        # Extract skills
        skills = extract_skills_from_job(title, description)
        
        # Create records for hard skills
        for hard_skill in skills.get('hard_skills', []):
            skill_records.append({
                'job_id': job_id,
                'hard_skill': hard_skill,
                'soft_skill': None
            })
        
        # Create records for soft skills
        for soft_skill in skills.get('soft_skills', []):
            skill_records.append({
                'job_id': job_id,
                'hard_skill': None,
                'soft_skill': soft_skill
            })
    
    return skill_records
