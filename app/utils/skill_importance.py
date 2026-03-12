# utils/skill_importance.py

FREQUENCY_THRESHOLD = 0.05

def importance_tier(score: float) -> str:
    if score >= 2.0:
        return "required"
    elif score >= 1.0:
        return "recommended"
    return "optional"

def is_meaningful(importance: str, freq: float | None) -> bool:
    if importance == "required":
        return True
    if importance == "recommended":
        return (freq or 0) >= FREQUENCY_THRESHOLD
    return False

def should_include(freq: float | None, importance: str) -> bool:
    if importance in ("required", "recommended"):
        return True
    return (freq or 0) >= FREQUENCY_THRESHOLD
