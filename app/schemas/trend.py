# app/schemas/trend.py
from pydantic import BaseModel
from typing import List, Optional, Any


class JobTrendItem(BaseModel):
    sub_category: str
    job_count: int


class SkillTrendItem(BaseModel):
    id: int
    skill: str
    count: int
    skill_type: str


class CrossDataResponse(BaseModel):
    filter: Optional[dict]
    type: str
    data: Optional[List[Any]] = None
    job_trend: Optional[List[JobTrendItem]] = None
    skill_trend: Optional[List[SkillTrendItem]] = None