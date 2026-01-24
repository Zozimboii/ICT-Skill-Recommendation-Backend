# app/schemas/positions.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class PositionItem(BaseModel):
    id: str
    name: str
    main_category_id: int
    main_category_name: str
    job_count: int

class PositionSkill(BaseModel):
    skill_name: str
    count: int
    weight: int  # 0-100
    demand_level: Literal["HIGH", "MEDIUM", "LOW"]
    demand_label: str

class PositionSkillsResponse(BaseModel):
    position_id: str
    position_name: str
    total_jobs: int
    skills: List[PositionSkill]

class UserSkillScore(BaseModel):
    skill_name: str
    score: int = Field(ge=0, le=5)  # ให้คะแนน 0-5

class GapItem(BaseModel):
    skill_name: str
    gap: int  # 0-100

class MatchResponse(BaseModel):
    position_id: str
    position_name: str
    match_percent: int
    labels: List[str]
    user_data: List[int]
    job_data: List[int]
    gaps: List[GapItem]
