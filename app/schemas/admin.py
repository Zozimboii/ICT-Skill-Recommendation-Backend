# app/schemas/admin.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AdminStats(BaseModel):
    total_users: int
    total_jobs: int
    total_skills: int
    total_transcripts: int


class AdminUserItem(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None


class AdminJobItem(BaseModel):
    id: int
    title: str
    company_name: str
    location: Optional[str]
    sub_category: Optional[str]
    posted_date: Optional[str]
    skill_count: int = 0

    class Config:
        from_attributes = True


class AdminSkillItem(BaseModel):
    id: int
    name: str
    skill_type: str
    job_count: int = 0

    class Config:
        from_attributes = True


class AdminSkillCreate(BaseModel):
    name: str
    skill_type: str  # "hard_skill" | "soft_skill"


class ScrapeRequest(BaseModel):
    limit: int = 50


class ScrapeResponse(BaseModel):
    message: str
    jobs_added: int