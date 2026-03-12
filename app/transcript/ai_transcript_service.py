# app/services/transcript_match/ai_transcript_service.py
import json
import os
import re
import time
import google.generativeai as genai
import google.api_core.exceptions


class AITranscriptService:
    
    RETRY_WAIT = 30

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))

    def _generate_with_retry(self, prompt: str, config: dict = None, retries: int = 2) -> str | None:
        for attempt in range(retries + 1):
            try:
                kwargs = {"generation_config": config} if config else {}
                resp = self.model.generate_content(prompt, **kwargs)
                return resp.text
            except google.api_core.exceptions.ResourceExhausted as e:
                delay_match = re.search(r'retry_delay \{\s*seconds: (\d+)', str(e))
                wait = int(delay_match.group(1)) + 2 if delay_match else self.RETRY_WAIT
                if attempt < retries:
                    print(f"[AI QUOTA] 429 — รอ {wait}s แล้ว retry ({attempt+1}/{retries})")
                    time.sleep(wait)
                else:
                    print(f"[AI QUOTA] quota หมด — ใช้ fallback parser")
                    return None
            except Exception as e:
                print(f"[AI ERROR] {type(e).__name__}: {e}")
                return None

    def parse_transcript(self, text: str) -> dict:
        """
        Parse transcript → structured dict
        ถ้า AI quota หมด → fallback rule-based parser
        """
        EMPTY = {
            "gpa": None, "university": "", "major": "",
            "skills": [], "courses": [], "ai_status": "quota_exceeded"
        }

        try:
            cleaned = re.sub(r"\s+", " ", text).strip()[:6000]

            prompt = f"""You are an expert academic transcript parser specializing in Thai university transcripts.
Your task is to extract structured data from the transcript text provided.

CONTEXT:
- This is a Thai university academic transcript (ใบรายงานผลการศึกษา)
- Course codes follow patterns like: CPE101, CS301, 01418101, EN101
- Thai grading: A, B+, B, C+, C, D+, D, F, S, U, W, P
- GPA scale: 0.00 – 4.00
- Credits are typically 1–4 per course
- University name may appear as Thai or English
- Major/Faculty may be in Thai (คณะ/สาขา) or English

EXTRACTION RULES:
1. Extract ALL courses found — do not skip any row
2. For course_name: use the English name if both exist, otherwise Thai is fine
3. For GPA: look for คะแนนเฉลี่ยสะสม, GPA, GPAX, or similar — take the FINAL cumulative GPA
4. For skills: extract any technical skills, tools, or programming languages explicitly mentioned
5. If a field is not found, use null for numbers and "" for strings

Return STRICTLY VALID JSON only. No markdown. No explanation. No backticks.

SCHEMA:
{{
  "gpa": number | null,
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

TRANSCRIPT TEXT:
{cleaned}"""

            raw = self._generate_with_retry(prompt, config={"temperature": 0.0})

            if raw is None:
                print("[TRANSCRIPT] AI unavailable — switching to rule-based parser")
                from app.utils.transcript_parser_fallback import parse_transcript_fallback
                return parse_transcript_fallback(text)

            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

            parsed = json.loads(raw)

            # Validate
            if not isinstance(parsed.get("courses"), list):
                parsed["courses"] = []
            if not isinstance(parsed.get("skills"), list):
                parsed["skills"] = []

            parsed["ai_status"] = "success"
            print(f"[AI TRANSCRIPT] parsed: gpa={parsed.get('gpa')} "
                  f"courses={len(parsed.get('courses', []))} "
                  f"skills={len(parsed.get('skills', []))}")
            return parsed

        except json.JSONDecodeError as e:
            print(f"[AI PARSE ERROR] JSON decode failed: {e} — trying fallback")
            from app.utils.transcript_parser_fallback import parse_transcript_fallback
            return parse_transcript_fallback(text)
        except Exception as e:
            print(f"[AI ERROR] parse_transcript: {e}")
            return EMPTY

    @staticmethod
    def validate_gpa(gpa) -> float:
        if gpa is None:
            return 0.0
        try:
            gpa = float(gpa)
        except (ValueError, TypeError):
            return 0.0
        return round(gpa, 2) if 0 <= gpa <= 4 else 0.0