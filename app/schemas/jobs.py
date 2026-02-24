from pydantic import BaseModel
from typing import List, Optional


class LocationResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class JobDataResponse(BaseModel):
    id: int
    title: str
    link: str
    posted_at_text: str
    description: Optional[str] = None
    location: Optional[LocationResponse] = None

    class Config:
        from_attributes = True


class RecommendResponse(BaseModel):
    job_id: int
    title: str
    soft_skills: List[str]
    hard_skills: List[str]
