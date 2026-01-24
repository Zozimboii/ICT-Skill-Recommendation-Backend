from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.skills_service import search_skill
from app.schemas.skills import SkillSearchResponse

router = APIRouter()

@router.get("/search", response_model=SkillSearchResponse)
def skill_search(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return search_skill(db, keyword=q, limit=limit)

