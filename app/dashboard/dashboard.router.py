# app/api/v1/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session



from app.models.user import User
from app.services import dashboard_service
from app.schemas.dashboard import DashboardSummary, SkillGapResponse, RecommendationItem
from app.core.database import get_db
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_service.get_summary(db, current_user.id)


@router.get("/skill-gap", response_model=list[SkillGapResponse])
def get_skill_gap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_service.get_skill_gap(db, current_user.id)


@router.get("/recommendations", response_model=list[RecommendationItem])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_service.get_recommendations(db, current_user.id)