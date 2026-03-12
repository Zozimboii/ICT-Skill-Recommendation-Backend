# app/schemas/assessment.py
from pydantic import BaseModel
from typing import Optional


class PositionItem(BaseModel):
    id: str
    name: str
    job_count: int


class PositionSkillItem(BaseModel):
    skill_id: int
    skill_name: str
    skill_type: str          # hard_skill | soft_skill
    weight: int              # 0-100 (normalized)
    job_count: int           # จำนวน jobs ที่ใช้ skill นี้
    frequency: int           # % ของ jobs ใน position ที่ต้องการ skill นี้


class PositionSkillsResponse(BaseModel):
    position_id: str
    position_name: str
    total_jobs: int
    skills: list[PositionSkillItem]


class SkillScoreInput(BaseModel):
    skill_id: int
    score: float             # 0-5


class SaveAssessmentRequest(BaseModel):
    sub_category_id: int
    skill_scores: list[SkillScoreInput]