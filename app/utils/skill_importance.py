# app/utils/skill_importance.py
"""
ใช้ frequency_score แทน importance_score เพราะ:
- importance_score ใน DB ไม่น่าเชื่อถือ (scraper assign 0.5 ให้ hard skill ทุกตัว)
- frequency_score = % ของ jobs ที่ต้องการ skill = market demand จริง

Thresholds:
  required    → freq >= 50%  (ปรากฏใน job มากกว่าครึ่ง)
  recommended → freq >= 20%  (ปรากฏบ่อย แต่ไม่จำเป็น)
  optional    → freq < 20%
"""

FREQ_REQUIRED    = 0.50   # >= 50% → required
FREQ_RECOMMENDED = 0.20   # >= 20% → recommended
FREQ_THRESHOLD   = 0.10   # < 10% → ตัดทิ้ง (noise)


def importance_tier(score: float) -> str:
    """
    score ที่รับเข้ามาคือ importance_score จาก JobSkill
    แต่เราไม่ใช้ค่านี้ตัดสินแล้ว — ใช้ frequency_score แทน
    เก็บ function signature เดิมไว้เพื่อ backward compat
    """
    # legacy mapping (ไม่ใช้แล้วใน logic ใหม่)
    if score >= 2.0:
        return "required"
    elif score >= 1.0:
        return "recommended"
    return "optional"


def importance_tier_by_freq(freq: float | None) -> str:
    """
    ตัดสิน importance จาก frequency_score (0.0-1.0)
    นี่คือ function หลักที่ควรใช้ใน dashboard_service
    """
    f = freq or 0.0
    if f >= FREQ_REQUIRED:
        return "required"
    elif f >= FREQ_RECOMMENDED:
        return "recommended"
    return "optional"


def is_meaningful(importance: str, freq: float | None) -> bool:
    """skill นี้ควร count ใน match score ไหม"""
    f = freq or 0.0
    if importance == "required":
        return True
    if importance == "recommended":
        return f >= FREQ_THRESHOLD
    return False


def should_include(freq: float | None, importance: str) -> bool:
    """skill นี้ควรแสดงใน missing list ไหม"""
    f = freq or 0.0
    if importance in ("required", "recommended"):
        return f >= FREQ_THRESHOLD   # ตัดแค่ noise จริงๆ
    return f >= FREQ_THRESHOLD