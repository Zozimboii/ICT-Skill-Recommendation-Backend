# utils/grade_confidence.py

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
    "W":   0.00,
    "S":   0.70,
    "U":   0.00,
    "P":   0.70,
}

SOURCE_WEIGHT = {
    "db_match": 0.85,
    "ai_infer": 0.65,
}

MIN_CONFIDENCE = 0.10


def grade_to_confidence(grade: str, source: str) -> float:
    grade_clean = (grade or "").strip().upper()
    grade_score = GRADE_SCORE.get(grade_clean, 0.50)
    weight = SOURCE_WEIGHT.get(source, 0.60)
    confidence = grade_score * weight

    if source == "db_match":
        confidence = max(confidence, MIN_CONFIDENCE)

    return round(confidence, 3)