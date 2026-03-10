# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Optional


class DashboardSummary(BaseModel):
    gpa: Optional[float] = None
    university: Optional[str] = None
    major: Optional[str] = None
    hard_skill_count: int = 0
    soft_skill_count: int = 0
    recommendation_count: int = 0
    has_transcript: bool = False


class SkillGapItem(BaseModel):
    skill_name: str
    skill_type: str
    status: str                  # "matched" | "missing"
    importance: str = "optional" # "required" | "recommended" | "optional"
    frequency_score: Optional[float] = None  # Phase 3


class SkillGroupItem(BaseModel):
    group_name: str
    skills: List[SkillGapItem]
    count: int


# Phase 3: Career Path step
class CareerPathStep(BaseModel):
    step: int
    title: str
    group: str
    skills: List[str]
    priority: str   # "required" | "recommended" | "optional"


class SkillGapResponse(BaseModel):
    job_title: str
    company_name: str
    sub_category: Optional[str]
    match_score: float
    skill_match_percent: float
    matched_skills: List[SkillGapItem]
    missing_skills: List[SkillGapItem]       # top 10 flat
    missing_by_group: List[SkillGroupItem]   # Phase 2
    career_path: List[CareerPathStep]        # Phase 3
    total_missing: int
    total_job_skills: int
    matched_count: int
    missing_group_count: int = 0


class RecommendationItem(BaseModel):
    id: int
    job_id: int
    title: str
    company_name: str
    location: Optional[str]
    sub_category: Optional[str]
    match_score: float
    skill_match_percent: float
    matched_count: int = 0
    total_skill_count: int = 0