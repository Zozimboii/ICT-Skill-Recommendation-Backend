from pydantic import BaseModel
from typing import List, Literal

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