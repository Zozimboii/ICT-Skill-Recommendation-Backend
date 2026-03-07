# app/services/ai_transcript_service.py

import json
import os
import re
import google.generativeai as genai
from sqlalchemy.orm import Session

from app.model.ai_model import AITranscriptLog

class AITranscriptService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            os.getenv("GEMINI_MODEL")
        )
    def infer_skills_from_courses(
        self,
        db: Session,
        transcript,
        course_names: list[str],
        model
    ) -> dict:

        prompt = f"""
        Given these courses:
        {course_names}

        Return JSON format:
        [
          {{
            "course": "...",
            "skills": ["skill1", "skill2"]
          }}
        ]

        Only choose skills relevant to ICT domain.
        """

        response = self.model.generate_content(prompt)

        parsed = json.loads(response.text)

        # log
        log = AITranscriptLog(
          transcript_id=transcript.id,
          model_id=model.id,  # 🔥 เพิ่มตรงนี้
          raw_response=parsed,
          token_used=response.usage_metadata.total_token_count,
          status="success"
        )

        db.add(log)


        return parsed
    
    @staticmethod
    def validate_gpa(gpa: float) -> float:
        if gpa is None:
            return 0.0
        
        try:
            gpa = float(gpa)
        except (ValueError, TypeError):
            return 0.0
    
        if 0 <= gpa <= 4:
            return gpa
        
        return 0.0
    def parse_transcript(self, text: str):

        try:
            text = re.sub(r"\s+", " ", text)
            text = text[:6000]

            prompt = f"""
                You are a JSON extraction engine.

                Return STRICTLY VALID JSON.
                No explanation.
                No markdown.
                No backticks.
                No extra text.

                SCHEMA:
                {{
                  "gpa": number,
                  "university": string,
                  "major": string,
                  "skills": string[],
                  "courses": [
                    {{
                      "course_code": string,
                      "course_name": string,
                      "grade": string,
                      "credit": number
                    }}
                  ]
                }}

                Transcript:
                {text}
                """

            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.1}
            )

            raw_text = response.text.strip()

            # 🔥 remove markdown wrapper safely
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "")
                raw_text = raw_text.replace("```", "")
                raw_text = raw_text.strip()

            parsed = json.loads(raw_text)

            # safety check
            if not isinstance(parsed.get("courses"), list):
                parsed["courses"] = []

            return parsed

        except Exception as e:
            print("AI ERROR:", e)

            return {
                "gpa": None,
                "university": "",
                "major": "",
                "skills": [],
                "courses": [],
                "ai_status": "failed"
            }
    # def parse_transcript(self, text: str):
    
    #     try:
    #         text = text[:6000]
    
    #         prompt = f"""
    #                 You are a JSON extraction engine.

    #                 Return STRICTLY VALID JSON.
    #                 No explanation.
    #                 No markdown.
    #                 No backticks.
    #                 No extra text.

    #                 If any field is missing, return empty value.

    #                 SCHEMA:
    #                 {{
    #                   "gpa": number,
    #                   "university": string,
    #                   "major": string,
    #                   "skills": string[],
    #                   "courses": [
    #                     {{
    #                       "course_code": string,
    #                       "course_name": string,
    #                       "grade": string,
    #                       "credit": number
    #                     }}
    #                   ]
    #                 }}

    #                 Transcript:
    #                 {text}
    #                 """
    
    #         response = self.model.generate_content(
    #             prompt,
    #             generation_config={
    #                 "temperature": 0.1
    #             }
    #         )
    
    #         raw_text = response.text.strip()
    
    #         print("RAW AI RESPONSE:")
    #         print(raw_text)
    
    #         # ✅ ดึงเฉพาะ JSON block
    #         json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    #         if not json_match:
    #             raise Exception("No JSON found in AI response")
    
    #         clean_json = json_match.group()
    
    #         return json.loads(clean_json)
    
    #     except Exception as e:
    #         print("AI ERROR:", e)
    #         return {
    #             "gpa": 0.0,
    #             "university": "",
    #             "major": "",
    #             "skills": [],
    #             "courses": []
    #         }