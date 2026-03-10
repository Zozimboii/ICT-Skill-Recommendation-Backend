# app/services/transcript_match/transcript_service.py

from sqlalchemy.orm import Session
from app.model.transcript import Transcript, TranscriptCourse


class TranscriptService:

    def create_transcript(
        self,
        db: Session,
        user_id: int,
        parsed_text: str,
        gpa: float = None,
        university: str = None,
        major: str = None,
        file_path: str = None
    ) -> Transcript:

        transcript = Transcript(
            user_id=user_id,
            parsed_text=parsed_text,
            gpa=gpa,
            university=university,
            major=major,
            file_path=file_path
        )
        db.add(transcript)
        db.flush()  
        db.refresh(transcript)
        return transcript

    def extract_courses(
        self,
        db: Session,
        transcript: Transcript,
        course_list: list[dict]
    ):
        for c in course_list:
            course = TranscriptCourse(
                transcript_id=transcript.id,
                course_code=c.get("course_code", ""),
                course_name=c.get("course_name", ""),
                grade=c.get("grade", ""),
                credit=float(c.get("credit") or 0)
            )
            db.add(course)

        db.flush()   # ✅ flush แทน commit