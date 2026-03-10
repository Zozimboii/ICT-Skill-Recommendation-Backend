# app/utils/career_path.py
"""
Phase 3 — ข้อ 4: สร้าง Career Path / Roadmap
Logic: จัดเรียง missing skills เป็น steps ตาม
  1. importance_score (required ก่อน)
  2. skill group dependency order (Cloud ก่อน Programming ก่อน Management)
  3. frequency_score (ที่ market ต้องการมากก่อน)
"""

from app.utils.skill_groups import get_skill_group

# ลำดับความสำคัญของ group (เรียนอะไรก่อน)
GROUP_ORDER = {
    "Programming":              1,
    "Cloud & Infrastructure":   2,
    "Data & Analytics":         3,
    "Security":                 4,
    "Design & UX":              5,
    "Management & Soft Skills": 6,
    "Other":                    7,
}

# ชื่อ step ที่ user เข้าใจง่าย
GROUP_STEP_LABEL = {
    "Programming":              "Build Core Programming Skills",
    "Cloud & Infrastructure":   "Learn Cloud & Infrastructure",
    "Data & Analytics":         "Master Data & Analytics",
    "Security":                 "Develop Security Knowledge",
    "Design & UX":              "Learn Design & UX",
    "Management & Soft Skills": "Develop Leadership & Management Skills",
    "Other":                    "Learn Specialized Skills",
}


def build_career_path(missing_skills: list[dict], max_steps: int = 5) -> list[dict]:
    """
    missing_skills: list of {
        skill_name: str,
        importance: str,     # "required" | "recommended" | "optional"
        frequency_score: float | None,
    }

    returns: list of steps [
        {
            step: int,
            title: str,
            group: str,
            skills: list[str],
            priority: str,   # "required" | "recommended" | "optional"
        }
    ]
    """
    if not missing_skills:
        return []

    # กรอง optional + low frequency ออก (ข้อ 9)
    filtered = [
        s for s in missing_skills
        if s.get("importance") != "optional"
        or (s.get("frequency_score") or 0) >= 0.05  # >= 5% frequency
    ]

    # จัดกลุ่มตาม group
    grouped: dict[str, list[dict]] = {}
    for skill in filtered:
        group = get_skill_group(skill["skill_name"])
        grouped.setdefault(group, []).append(skill)

    # เรียง group ตาม GROUP_ORDER แล้วตัดแค่ max_steps
    sorted_groups = sorted(
        grouped.items(),
        key=lambda x: (
            # required group ก่อน
            0 if any(s["importance"] == "required" for s in x[1]) else 1,
            GROUP_ORDER.get(x[0], 99),
        ),
    )[:max_steps]

    steps = []
    for i, (group, skills) in enumerate(sorted_groups, 1):
        # เรียง skills ใน step: required → recommended → optional, แล้ว frequency desc
        skills_sorted = sorted(
            skills,
            key=lambda s: (
                0 if s["importance"] == "required" else
                1 if s["importance"] == "recommended" else 2,
                -(s.get("frequency_score") or 0),
            ),
        )

        # priority ของ step = importance ของ skill แรกใน step
        priority = skills_sorted[0]["importance"] if skills_sorted else "optional"

        steps.append({
            "step": i,
            "title": GROUP_STEP_LABEL.get(group, f"Learn {group}"),
            "group": group,
            "skills": [s["skill_name"] for s in skills_sorted[:6]],  # max 6 per step
            "priority": priority,
        })

    return steps