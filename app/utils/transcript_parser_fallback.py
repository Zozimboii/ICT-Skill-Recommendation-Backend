# app/utils/transcript_parser_fallback.py
"""
Rule-based transcript parser — ใช้เมื่อ AI quota หมด
รองรับ Thai university transcript format ทั่วไป
"""
import re


# GPA patterns
_GPA_PATTERNS = [
    r'(?:GPAX|GPA|คะแนนเฉลี่ยสะสม|ผลการเรียนเฉลี่ย)[^\d]*(\d+\.\d{2})',
    r'(?:cumulative|สะสม)[^\d]*(\d+\.\d{2})',
    r'\b([0-3]\.\d{2}|4\.00)\b',   # fallback: หาตัวเลข 0.xx–4.00
]

# Course row patterns (รองรับหลาย format)
_COURSE_PATTERNS = [
    # Format 1: CODE  Name  Grade  Credit  (standard Thai university)
    re.compile(
        r'\b([A-Z]{2,6}\s?\d{3,6})\s+'   # course code
        r'(.{5,60}?)\s+'                   # course name (5-60 chars)
        r'([A-DF][+\-]?|S|U|W|P)\s+'      # grade
        r'(\d+(?:\.\d)?)\b',               # credit
        re.MULTILINE
    ),
    # Format 2: ตัวเลขล้วน เช่น 01418101
    re.compile(
        r'\b(\d{7,9})\s+'
        r'(.{5,60}?)\s+'
        r'([A-DF][+\-]?|S|U|W|P)\s+'
        r'(\d+(?:\.\d)?)\b',
        re.MULTILINE
    ),
]

# University name hints
_UNIVERSITY_HINTS = [
    (r'มหาวิทยาลัย\s*\S+',             None),   # ดึงชื่อไทย
    (r'university\s+of\s+\S+',          None),
    (r'\b\S+\s+university\b',           None),
    (r'institute\s+of\s+technology',    None),
    (r'สถาบัน\S+',                      None),
]

# Faculty/Major hints
_MAJOR_HINTS = [
    r'(?:สาขา|สาขาวิชา)[^\n:]{0,5}[:\s]+([^\n]{3,60})',
    r'(?:major|program(?:me)?)[:\s]+([^\n]{3,60})',
    r'(?:คณะ)[^\n:]{0,5}[:\s]+([^\n]{3,60})',
    r'(?:faculty|department)[:\s]+([^\n]{3,60})',
    r'(?:วิศวกรรม\S+|วิทยาการ\S+|วิทยาศาสตร์\S+|เทคโนโลยี\S+)',
]


def parse_transcript_fallback(text: str) -> dict:
    """
    Rule-based parser — ไม่ต้องใช้ AI
    return dict เหมือน AITranscriptService.parse_transcript()
    """
    print("[FALLBACK PARSER] starting rule-based parse")

    result = {
        "gpa":        _extract_gpa(text),
        "university": _extract_university(text),
        "major":      _extract_major(text),
        "skills":     [],
        "courses":    _extract_courses(text),
        "ai_status":  "fallback",
    }

    print(f"[FALLBACK PARSER] done — "
          f"gpa={result['gpa']} "
          f"university='{result['university']}' "
          f"courses={len(result['courses'])}")
    return result


def _extract_gpa(text: str) -> float | None:
    for pattern in _GPA_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            candidates = [float(m) for m in matches if 0 <= float(m) <= 4.0]
            if candidates:
                # เอา GPA ที่เจอล่าสุด (มักเป็น cumulative)
                return candidates[-1]
    return None


def _extract_university(text: str) -> str:
    # Thai university names
    m = re.search(r'มหาวิทยาลัย[\s\S]{0,30}?(?=\n|$|\s{2,})', text)
    if m:
        return m.group(0).strip()[:80]

    # English
    m = re.search(r'(?:university|institute)[^\n]{0,50}', text, re.IGNORECASE)
    if m:
        return m.group(0).strip()[:80]

    return ""


def _extract_major(text: str) -> str:
    for pattern in _MAJOR_HINTS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            name = (groups[0] if groups else m.group(0)).strip()
            if 3 <= len(name) <= 80:
                return name
    return ""


def _extract_courses(text: str) -> list[dict]:
    courses = []
    seen_codes = set()

    for pattern in _COURSE_PATTERNS:
        for match in pattern.finditer(text):
            code   = match.group(1).strip().replace(" ", "")
            name   = match.group(2).strip()
            grade  = match.group(3).strip().upper()
            credit = match.group(4).strip()

            # skip duplicate
            if code in seen_codes:
                continue

            # skip noise (name too short or looks like numbers)
            if len(name) < 4 or name.isdigit():
                continue

            seen_codes.add(code)
            courses.append({
                "course_code": code,
                "course_name": name,
                "grade":       grade,
                "credit":      float(credit),
            })

    # sort by course_code
    courses.sort(key=lambda x: x["course_code"])
    return courses