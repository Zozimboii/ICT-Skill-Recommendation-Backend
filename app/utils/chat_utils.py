from typing import List

from sqlalchemy.orm import Session

from app.db.models import JobCountBySubCategory


def extract_subcategories_from_answer(
    text: str,
    db: Session
) -> List[str]:

    lower = text.lower()

    # ดึง subcategory ทั้งหมดจาก DB
    subcats = db.query(JobCountBySubCategory.sub_category_name).all()

    found = []

    for (name,) in subcats:
        if name.lower() in lower:
            found.append(name)

    return found[:8]  # limit chip ไม่ให้เยอะเกิน
