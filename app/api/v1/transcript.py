# app/api/v1/transcirpt.py
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session


from app.model.user import User

from app.core.database import get_db
from app.services.transcript_match.transcript_proessing_service import TranscriptProcessingService
from app.core.deps import get_current_user
from app.model.skill import Skill, UserSkill
from app.model.transcript import Transcript, TranscriptCourse
from app.schemas.transcript import TranscriptDetailOut
from app.model.job import Job
from app.model.recommendation import Recommendation

router = APIRouter()

@router.post("/upload-transcript")
async def upload_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TranscriptProcessingService()
    transcript = service.process_pdf(
        db=db,
        file=file,
        user_id=current_user.id
    )
    return {"message": "Transcript processed", "id": transcript.id}


@router.get("/profile", response_model=TranscriptDetailOut)
def get_my_transcript(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transcript = (
        db.query(Transcript)
        .filter(Transcript.user_id == current_user.id)
        .order_by(Transcript.id.desc())
        .first()
    )

    if not transcript:
        raise HTTPException(status_code=404, detail="No transcript found")

    courses = (
        db.query(TranscriptCourse)
        .filter(TranscriptCourse.transcript_id == transcript.id)
        .all()
    )

    return {
        "id": transcript.id,
        "university": transcript.university,
        "major": transcript.major,
        "gpa": transcript.gpa,
        "courses": [
            {
                "course_code": c.course_code,
                "course_name": c.course_name,
                "grade": c.grade,
                "credit": c.credit,
            }
            for c in courses
        ],
    }


@router.get("/profile/skills")
def get_my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .filter(
            UserSkill.user_id == current_user.id,
            UserSkill.source == "transcript",
        )
        .order_by(UserSkill.confidence_score.desc())
        .all()
    )

    return [
        {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "skill_type": skill.skill_type,
            "confidence_score": user_skill.confidence_score,
        }
        for user_skill, skill in rows
    ]


@router.get("/profile/recommendations")
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Recommendation, Job)
        .join(Job, Recommendation.job_id == Job.id)
        .filter(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.skill_match_percent.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "id": rec.id,
            "job_id": job.id,
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location,
            "sub_category": job.sub_category.name if job.sub_category else None,
            "match_score": round(rec.match_score, 2),
            "skill_match_percent": round(rec.skill_match_percent, 1),
        }
        for rec, job in rows
    ]