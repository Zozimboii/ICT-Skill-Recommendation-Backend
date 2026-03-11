# app/services/transcript_processing_service.py

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.utils.file_utils import extract_text_from_pdf, save_file
from app.services.transcript_match.transcript_service import TranscriptService
from app.services.transcript_match.ai_transcript_service import AITranscriptService
from app.services.transcript_match.recommendation_engine import RecommendationEngine
from app.services.transcript_match.skill_matching_engine import SkillMatchingEngine
from app.models.transcript import Transcript
from app.models.skill import UserSkill


# ── Grade → score (0.0–1.0) ──────────────────────────────────────────────────
# สะท้อนความเชี่ยวชาญจริงจากผลการเรียน
GRADE_SCORE: dict[str, float] = {
    "A":   1.00,
    "A-":  0.93,
    "B+":  0.87,
    "B":   0.75,
    "B-":  0.68,
    "C+":  0.62,
    "C":   0.50,
    "C-":  0.43,
    "D+":  0.37,
    "D":   0.25,
    "F":   0.00,
    "W":   0.00,   # Withdraw
    "S":   0.70,   # Satisfactory (ไม่มี grade จริง ประมาณ B)
    "U":   0.00,   # Unsatisfactory
    "P":   0.70,   # Pass
}

# ── Source weight ─────────────────────────────────────────────────────────────
# ปรับ confidence ตาม "ความมั่นใจ" ของ source ที่ match ได้
SOURCE_WEIGHT = {
    "db_match":  0.85,   # skill.name ตรงใน course_name → มั่นใจสูง
    "ai_infer":  0.65,   # AI infer จากชื่อวิชา → น่าจะรู้ แต่ไม่ฟันธง
}

# ── Confidence floor ──────────────────────────────────────────────────────────
# แม้เกรด F ก็เคยเรียนผ่านมา — ให้ minimum 0.1 สำหรับ db_match
MIN_CONFIDENCE = 0.10


def grade_to_confidence(grade: str, source: str) -> float:
    """
    คำนวณ confidence จาก grade × source_weight
    เช่น grade=A, source=db_match → 1.0 × 0.85 = 0.85
         grade=C, source=ai_infer → 0.5 × 0.65 = 0.325
    """
    grade_clean = (grade or "").strip().upper()
    grade_score = GRADE_SCORE.get(grade_clean, 0.50)  # default 0.5 ถ้าไม่รู้ grade
    weight = SOURCE_WEIGHT.get(source, 0.60)
    confidence = grade_score * weight

    if source == "db_match":
        confidence = max(confidence, MIN_CONFIDENCE)

    return round(confidence, 3)


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