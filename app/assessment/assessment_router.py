# app/assessment/assessment_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.assessment.assessment_schema import PositionItem, PositionSkillsResponse, SaveAssessmentRequest
from app.assessment.assessment_service import AssessmentService

router = APIRouter()
assessment_service = AssessmentService()


# ── Public endpoints (guest เข้าได้) ─────────────────────────────────────────

@router.get("/positions", response_model=list[PositionItem])
def list_positions(
    db: Session = Depends(get_db),
    # ❌ ไม่ require auth — guest ดูได้
):
    return assessment_service.get_positions(db)


@router.get("/positions/{sub_category_id}/skills", response_model=PositionSkillsResponse)
def get_position_skills(
    sub_category_id: int,
    db: Session = Depends(get_db),
    # ❌ ไม่ require auth — guest ดูได้
):
    result = assessment_service.get_position_skills(db, sub_category_id)
    if not result:
        raise HTTPException(status_code=404, detail="Position not found")
    return result


# ── Protected endpoints (ต้อง login) ─────────────────────────────────────────

@router.post("/save")
def save_assessment(
    body: SaveAssessmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),  # ✅ require auth
):
    scores = [s.model_dump() for s in body.skill_scores]
    count = assessment_service.save_assessment_skills(db, current_user.id, scores)
    return {"saved": True, "count": count, "message": f"บันทึก {count} skills เรียบร้อย"}


@router.delete("/reset")
def reset_assessment(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),  # ✅ require auth
):
    count = assessment_service.reset_assessment_skills(db, current_user.id)
    return {"reset": True, "deleted": count}