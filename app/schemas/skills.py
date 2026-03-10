# app/schemas/skills.py

from pydantic import BaseModel
from typing import List, Literal, Optional


class SkillItem(BaseModel):
    skill_name: str
    skill_type: Literal["soft_skill", "hard_skill"]

