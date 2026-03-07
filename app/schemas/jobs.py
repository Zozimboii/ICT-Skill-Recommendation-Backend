
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class SkillOut(BaseModel):
    id: int
    name: str
    skill_type: str

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: int
    title: str
    company_name: str
    location: Optional[str] = None
    description: Optional[str] = None
    sub_category: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    posted_date: Optional[str] = None
    url: Optional[str] = None
    skills: List[SkillOut] = []

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[JobOut]

class RecommendResponse(BaseModel):
    job_id: int
    title: str
    soft_skills: List[str]
    hard_skills: List[str]
