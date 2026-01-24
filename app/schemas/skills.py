# from typing import Literal
# from pydantic import BaseModel
from pydantic import BaseModel
from typing import List, Literal, Optional


class SkillItem(BaseModel):
    skill_name: str
    skill_type: Literal["soft_skill", "hard_skill"]
class TopSubCategory(BaseModel):
    main_category_id: int
    main_category_name: str
    sub_category_id: int
    sub_category_name: str
    count: int

class RelatedSkill(BaseModel):
    skill_name: str
    count: int

class SkillSearchResponse(BaseModel):
    skill_name: str
    skill_type: Optional[str] = ""
    job_count: int
    top_subcategories: List[TopSubCategory]
    related_skills: List[RelatedSkill]
