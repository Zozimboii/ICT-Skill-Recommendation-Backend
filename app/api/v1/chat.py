import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import get_ai_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_with_ai(payload: ChatRequest, db: Session = Depends(get_db)):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="คำถามไม่สามารถว่างได้")

    # TODO: ตรงนี้ค่อยไปดึง db_data จริง (ตาม logic extract_keywords ของคุณ)
    db_data = None

    provider = os.getenv("AI_PROVIDER", "openai").lower()
    use_ai = (
        bool(os.getenv("GEMINI_API_KEY"))
        if provider == "gemini"
        else bool(os.getenv("OPENAI_API_KEY"))
    )

    answer = get_ai_response(question, db_data, use_ai=use_ai)

    return ChatResponse(answer=answer, question=question, has_ai=use_ai)
