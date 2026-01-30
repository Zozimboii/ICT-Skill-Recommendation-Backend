from typing import List, Optional

from pydantic import BaseModel


class AdvisorRequest(BaseModel):
    question: str


class TrendPreview(BaseModel):
    skill_name: str
    skill_type: Optional[str] = None
    job_count: int


class AdvisorResponse(BaseModel):
    intent: str
    suggested_skills: List[str]
    detected_keywords: List[str]
    trend_preview: Optional[TrendPreview] = None


# class AdvisorResponse(BaseModel):
#     intent: str
#     suggested_skills: List[str]
#     detected_keywords: List[str]
#     trend_preview: Dict[str, Any]
