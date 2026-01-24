from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.advisor import AdvisorRequest, AdvisorResponse
from app.services.advisor_service import ask_advisor
from app.utils.advisor_rules import DEFAULT_SKILLS, detect_intent, extract_keywords

router = APIRouter()

@router.post("", response_model=AdvisorResponse)  # POST /api/v1/advisor
def advisor(payload: AdvisorRequest, db: Session = Depends(get_db)):
    return ask_advisor(db, payload)
