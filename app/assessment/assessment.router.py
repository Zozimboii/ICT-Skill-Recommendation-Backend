# app/api/v1/assessment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.assessment import (
    PositionItem,
    PositionSkillsResponse,
    SaveAssessmentRequest,
)
from app.services import assessment_service
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/positions", response_model=list[PositionItem])
def list_positions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return assessment_service.get_positions(db)


@router.get("/positions/{sub_category_id}/skills", response_model=PositionSkillsResponse)
def get_position_skills(
    sub_category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = assessment_service.get_position_skills(db, sub_category_id)
    if not result:
        raise HTTPException(status_code=404, detail="Position not found")
    return result


@router.post("/save")
def save_assessment(
    body: SaveAssessmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    scores = [s.model_dump() for s in body.skill_scores]
    count = assessment_service.save_assessment_skills(db, current_user.id, scores)
    return {"saved": True, "count": count, "message": f"บันทึก {count} skills เรียบร้อย"}


@router.delete("/reset")
def reset_assessment(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """ลบ assessment skills ทั้งหมดของ user + re-generate recommendations"""
    count = assessment_service.reset_assessment_skills(db, current_user.id)
    return {"reset": True, "deleted": count}