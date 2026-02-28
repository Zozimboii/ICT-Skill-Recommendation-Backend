from pydantic import BaseModel
from typing import List


class TranscriptSkillResponse(BaseModel):
    id: int
    username: str
    hard_skills: List[str]
    soft_skills: List[str]


class TranscriptUploadResponse(BaseModel):
    status: str
    message: str
    data: TranscriptSkillResponse


class TranscriptListResponse(BaseModel):
    status: str
    message: str
    data: List[TranscriptSkillResponse]


class TranscriptGetResponse(BaseModel):
    status: str
    message: str
    data: TranscriptSkillResponse