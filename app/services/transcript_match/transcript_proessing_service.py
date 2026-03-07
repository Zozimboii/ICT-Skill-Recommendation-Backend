# app/services/transcript_processing_service.py

from fastapi import UploadFile
from sqlalchemy.orm import Session


from app.utils.file_utils import extract_text_from_pdf, save_file
from app.services.transcript_match.transcript_service import TranscriptService
from app.services.transcript_match.ai_transcript_service import AITranscriptService
from app.services.transcript_match.recommendation_engine import RecommendationEngine
from app.services.transcript_match.skill_matching_engine import SkillMatchingEngine
from app.model.transcript import Transcript
from app.model.skill import UserSkill


class TranscriptProcessingService:

    def __init__(self):
        self.transcript_service = TranscriptService()
        self.skill_engine = SkillMatchingEngine()
        self.ai_service = AITranscriptService()
        self.recommendation_engine = RecommendationEngine()

    def process_pdf(self, db: Session, user_id: int, file: UploadFile):

        try:
            # ✅ ลบ transcript เก่า + user_skills เก่าจาก transcript ก่อนเลย
            old_transcript = db.query(Transcript).filter(
                Transcript.user_id == user_id
            ).first()
    
            if old_transcript:
                db.delete(old_transcript)  # cascade ลบ courses ด้วยถ้ามี relationship
                db.flush()    

            db.query(UserSkill).filter(
                UserSkill.user_id == user_id,
                UserSkill.source == "transcript"
            ).delete()
            db.flush()
            file_path = save_file(file)
            text = extract_text_from_pdf(file_path)
    
            parsed_data = self.ai_service.parse_transcript(text)
    
            gpa = self.ai_service.validate_gpa(parsed_data.get("gpa"))
            university = parsed_data.get("university", "")
            major = parsed_data.get("major", "")
            courses = parsed_data.get("courses", [])
            transcript = self.transcript_service.create_transcript(
                db=db,
                user_id=user_id,
                parsed_text=text,
                gpa=gpa,
                university=university,
                major=major,
                file_path=file_path
            )
    
            if courses:
                self.transcript_service.extract_courses(
                    db=db,
                    transcript=transcript,
                    course_list=courses
                )
    
                for course in courses:
                    course_name = course.get("course_name", "").lower()
    
                    matched_skills = self.skill_engine.match_from_dictionary(
                        db=db,
                        course_name=course_name
                    )
    
                    if matched_skills:
                        self.skill_engine.attach_user_skills(
                            db=db,
                            user_id=user_id,
                            skills=matched_skills,
                            source="transcript",
                            confidence=0.8
                        )
    
            self.recommendation_engine.generate_for_user(
                db=db,
                user_id=user_id
            )
    
            db.commit()  # ✅ commit ครั้งเดียวตรงนี้
    
            return transcript
    
        except Exception as e:
            db.rollback()
            print("PROCESS ERROR:", e)
            raise        

    def process_transcript(
        self,
        db: Session,
        user_id: int,
        parsed_text: str,
        course_list: list[dict],
        gpa: float = None,
        university: str = None,
        major: str = None,
        file_path: str = None,
        ai_model=None
    ):
        # 1️⃣ Create transcript
        transcript = self.transcript_service.create_transcript(
            db=db,
            user_id=user_id,
            parsed_text=parsed_text,
            gpa=gpa,
            university=university,
            major=major,
            file_path=file_path,
        )

        # 2️⃣ Save courses
        self.transcript_service.extract_courses(
            db=db,
            transcript=transcript,
            course_list=course_list
        )

        all_course_names = []
        unmatched_courses = []

        # 3️⃣ Dictionary Matching
        for course in course_list:

            course_name = course["course_name"]
            all_course_names.append(course_name)

            matched_skills = self.skill_engine.match_from_dictionary(
                db=db,
                course_name=course_name
            )

            if matched_skills:
                self.skill_engine.attach_user_skills(
                    db=db,
                    user_id=user_id,
                    skills=matched_skills,
                    source="transcript",
                    confidence=0.9
                )
            else:
                unmatched_courses.append(course_name)

        # 4️⃣ AI Matching (Batch)
        if ai_model and unmatched_courses:

            ai_result = self.ai_service.infer_skills_from_courses(
                db=db,
                transcript=transcript,
                course_names=unmatched_courses,
                model=ai_model
            )

            # ai_result format:
            # [
            #   { "course": "...", "skills": [...] }
            # ]

            for item in ai_result:

                skill_names = item["skills"]

                for skill_name in skill_names:

                    matched_skills = self.skill_engine.match_from_dictionary(
                        db=db,
                        course_name=skill_name
                    )

                    if matched_skills:
                        self.skill_engine.attach_user_skills(
                            db=db,
                            user_id=user_id,
                            skills=matched_skills,
                            source="ai",
                            confidence=0.7
                        )
        # 5️⃣ Generate Recommendation
        self.recommendation_engine.generate_for_user(
            db=db,
            user_id=user_id
        )
        return transcript