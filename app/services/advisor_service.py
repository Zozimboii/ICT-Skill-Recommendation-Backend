from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import JobSkillCountBySkillname
from app.schemas.advisor import AdvisorRequest
from app.utils.advisor_rules import DEFAULT_SKILLS, detect_intent, extract_keywords

def ask_advisor(db: Session, payload: AdvisorRequest):
    question = payload.question.strip()
    intent = detect_intent(question)
    detected = extract_keywords(question)
    suggested = DEFAULT_SKILLS.get(intent, DEFAULT_SKILLS["general"])

    trend_preview = None
    if detected:
        kw = detected[0]
        row = (
            db.query(
                JobSkillCountBySkillname.skill_name,
                JobSkillCountBySkillname.skill_type,
                JobSkillCountBySkillname.job_skill_count,
            )
            .filter(func.lower(JobSkillCountBySkillname.skill_name).like(f"%{kw}%"))
            .order_by(JobSkillCountBySkillname.job_skill_count.desc())
            .first()
        )
        if row:
            trend_preview = {
                "skill_name": row[0],
                "skill_type": row[1],
                "job_count": int(row[2]),
            }

    return {
        "intent": intent,
        "suggested_skills": suggested,
        "detected_keywords": detected,
        "trend_preview": trend_preview,
    }
