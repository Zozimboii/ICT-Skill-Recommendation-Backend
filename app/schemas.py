from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional

class SkillItem(BaseModel):
    skill_name: str
    skill_type: Literal["soft_skill", "hard_skill"]

class RecommendResponse(BaseModel):
    job_id: int
    title: str
    soft_skills: List[str]
    hard_skills: List[str]

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

## AI 
## Advisor

class AdvisorRequest(BaseModel):
    question: str

class AdvisorResponse(BaseModel):
    intent: str
    suggested_skills: List[str]
    detected_keywords: List[str]
    trend_preview: Dict[str, Any]  # เอาผล /skills/search มาใส่สั้น ๆ

class ChatRequest(BaseModel):
    question: str
    include_context: bool = True  # ต้องการให้ AI ใช้ข้อมูลจาก database หรือไม่

class ChatResponse(BaseModel):
    answer: str
    question: str
    has_ai: bool  # ใช้ AI จริงหรือ fallback