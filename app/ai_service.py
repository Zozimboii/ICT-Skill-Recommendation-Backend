import os
import json
import requests
from typing import Optional, Dict
from dotenv import load_dotenv
from pathlib import Path

# โหลด .env
base_path = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_path / '.env')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_response(question: str, db_data: Optional[Dict] = None, use_ai: bool = True) -> str:
    if not use_ai or not GEMINI_API_KEY:
        return "ขออภัย เกิดข้อผิดพลาดในการเชื่อมต่อ AI"

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    system_instruction = "คุณเป็นผู้ช่วยผู้เชี่ยวชาญด้านทักษะและอาชีพ ICT ตอบเป็นภาษาไทยที่กระชับและเป็นมิตร"
    
    if db_data:
        db_context = json.dumps(db_data, ensure_ascii=False, indent=2)
        prompt = f"{system_instruction}\n\nข้อมูลจากฐานข้อมูล:\n{db_context}\n\nคำถาม: {question}"
    else:
        prompt = f"{system_instruction}\n\nคำถาม: {question}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        result = response.json()

        if response.status_code == 200:
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            error_msg = result.get('error', {}).get('message', 'Unknown Error')
            print(f"❌ Gemini Direct API Error ({response.status_code}): {error_msg}")
            return "ขออภัย ระบบ AI ขัดข้องชั่วคราว"

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return "ไม่สามารถติดต่อ AI ได้ในขณะนี้ กรุณาลองใหม่ภายหลัง"