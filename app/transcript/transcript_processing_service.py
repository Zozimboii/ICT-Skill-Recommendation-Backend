# app/services/transcript_processing_service.py

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.utils.file_utils import extract_text_from_pdf, save_file

from app.models.transcript import Transcript
from app.models.skill import UserSkill
from app.transcript.ai_transcript_service import AITranscriptService
from app.transcript.recommendation_engine import RecommendationEngine
from app.transcript.skill_matching_engine import SkillMatchingEngine
from app.transcript.transcript_service import TranscriptService
from app.utils.grade_confidence import grade_to_confidence


class TranscriptProcessingService:

    def __init__(self):
        self.transcript_service = TranscriptService()
        self.skill_engine = SkillMatchingEngine()
        self.ai_service = AITranscriptService()
        self.recommendation_engine = RecommendationEngine()

    def process_pdf(self, db: Session, user_id: int, file: UploadFile):
        try:
            print(f"[TRANSCRIPT] ▶ start user_id={user_id}")

            # 1. ลบข้อมูลเก่า
            old_transcript = db.query(Transcript).filter(
                Transcript.user_id == user_id
            ).first()
            if old_transcript:
                db.delete(old_transcript)
                db.flush()
                print(f"[TRANSCRIPT] deleted old transcript id={old_transcript.id}")

            deleted = db.query(UserSkill).filter(
                UserSkill.user_id == user_id,
                UserSkill.source.in_(["transcript", "assessment"])
            ).delete()
            db.flush()
            print(f"[TRANSCRIPT] deleted {deleted} old user_skills")

            # 2. Extract PDF
            file_path = save_file(file)
            text = extract_text_from_pdf(file_path)
            print(f"[TRANSCRIPT] text length={len(text)}")

            # 3. AI parse
            parsed_data = self.ai_service.parse_transcript(text)
            gpa        = self.ai_service.validate_gpa(parsed_data.get("gpa"))
            university = parsed_data.get("university", "")
            major      = parsed_data.get("major", "")
            courses    = parsed_data.get("courses", [])
            ai_skills  = parsed_data.get("skills", [])   # skills ที่ AI extract โดยตรง
            print(f"[TRANSCRIPT] parsed gpa={gpa} university='{university}' courses={len(courses)} ai_skills={len(ai_skills)}")

            if not courses:
                print("[TRANSCRIPT] WARNING: no courses — AI อาจ fail หรือ PDF อ่านไม่ได้")

            # 4. สร้าง Transcript record
            transcript = self.transcript_service.create_transcript(
                db=db,
                user_id=user_id,
                parsed_text=text,
                gpa=gpa,
                university=university,
                major=major,
                file_path=file_path
            )
            print(f"[TRANSCRIPT] created transcript id={transcript.id}")

            # 5. courses + skill matching with grade-based confidence
            total_matched = 0
            if courses:
                self.transcript_service.extract_courses(
                    db=db,
                    transcript=transcript,
                    course_list=courses
                )
                print(f"[TRANSCRIPT] saved {len(courses)} courses")

                for course in courses:
                    course_name = course.get("course_name", "")
                    grade       = course.get("grade", "")

                    # strategy 1: direct → 2: course_map → 3: ai_skills (normalized)
                    matched_skills, source = self.skill_engine.match_skills(
                        db=db,
                        course_name=course_name,
                        ai_skills=ai_skills
                    )

                    if matched_skills:
                        # source weight: db_match=0.85, course_map=ai_infer=0.65
                        conf_source = "db_match" if source == "db_match" else "ai_infer"
                        confidence  = grade_to_confidence(grade, source=conf_source)

                        self.skill_engine.attach_user_skills(
                            db=db,
                            user_id=user_id,
                            skills=matched_skills,
                            source="transcript",
                            confidence=confidence
                        )
                        total_matched += len(matched_skills)
                        print(f"  [MATCH:{source}] '{course_name}' grade={grade} → {len(matched_skills)} skills conf={confidence}")

            print(f"[TRANSCRIPT] skills matched={total_matched}")

            # 6. Recommendations
            print("[TRANSCRIPT] generating recommendations...")
            recs = self.recommendation_engine.generate_for_user(
                db=db, user_id=user_id
            )
            print(f"[TRANSCRIPT] generated {len(recs)} recommendations")

            # 7. Single commit
            db.commit()
            print("[TRANSCRIPT] committed OK")

            return transcript

        except Exception as e:
            db.rollback()
            print(f"[TRANSCRIPT] ERROR {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise