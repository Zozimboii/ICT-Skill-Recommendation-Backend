from typing import List, Optional

from pydantic import BaseModel


class CourseOut(BaseModel):
    course_code: str
    course_name: str
    grade: str
    credit: float

    class Config:
        from_attributes = True


# Schema — ลบ created_at ออก
class TranscriptDetailOut(BaseModel):
    id: int
    university: Optional[str]
    major: Optional[str]
    gpa: Optional[float]
    courses: List[CourseOut] = []

    class Config:
        from_attributes = True

# แก้ Schema ให้ตรง
class SkillOut(BaseModel):
    skill_id: int
    skill_name: str
    skill_type: str
    confidence_score: float

    class Config:
        from_attributes = True