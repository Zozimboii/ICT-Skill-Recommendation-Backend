# app/services/transcript_service.py

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
        db.commit()
        db.refresh(transcript)

        return transcript


    def extract_courses(
        self,
        db: Session,
        transcript: Transcript,
        course_list: list[dict]
    ):
        """
        course_list = [
            {
                "course_code": "CS101",
                "course_name": "Data Structures",
                "grade": "A",
                "credit": 3.0
            }
        ]
        """

        for c in course_list:
            course = TranscriptCourse(
                transcript_id=transcript.id,
                course_code=c["course_code"],
                course_name=c["course_name"],
                grade=c["grade"],
                credit=c["credit"]
            )
            db.add(course)

        db.commit()