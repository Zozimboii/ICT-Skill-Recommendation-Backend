import os
from io import BytesIO
import traceback
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from pypdf import PdfReader
from docx import Document

from app.core.dependencies import get_current_user
from app.db.models import User

from app.db.database import get_db
from app.schemas.transcript import (
    TranscriptUploadResponse,
    TranscriptListResponse,
    TranscriptGetResponse,
)
from app.services.Transcript_service import (
    process_transcript_file,
    get_transcript_by_id,
    get_all_transcripts,
)

router = APIRouter()


@router.post("/upload", response_model=TranscriptUploadResponse)
async def upload_transcript(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # ✅ เช็ค filename ก่อน
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing"
            )

        # ✅ ตรวจสอบนามสกุลไฟล์
        allowed_extensions = {".txt", ".pdf"}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        # ✅ อ่านไฟล์
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # ✅ เรียก service
        result = process_transcript_file(
            db=db,
            username=current_user.username,
            file_name=file.filename,
            file_bytes=content,
            file_ext=file_ext
        )

        # ✅ return ให้ตรงกับ response_model
        return TranscriptUploadResponse(
            status="success",
            message=f"Successfully processed transcript: {file.filename}",
            data=result
        )

    except HTTPException:
        # ปล่อย HTTPException ผ่านไปตรง ๆ
        raise

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/list", response_model=TranscriptListResponse)
def list_transcripts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transcripts = get_all_transcripts(db)
    return TranscriptListResponse(
        status="success",
        message="Successfully retrieved transcripts",
        data=transcripts
    )