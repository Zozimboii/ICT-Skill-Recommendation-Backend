# app/utils/skill_extractor.py
import re

from app.utils.skill_dict import SKILL_DICT, SYNONYMS


def extract_skills(description: str):
    found = []
    if not description:
        return found, []

    text = description.lower()

    # Known skills
    for skill_key, skill_type in SKILL_DICT.items():
        if re.search(r"\b" + re.escape(skill_key.lower()) + r"\b", text):
            found.append((skill_key, skill_type))

    # Unknown skills detection
    unknown = detect_unknown_skills(description, SKILL_DICT.keys())

    return found, unknown


def normalize_skill(skill: str):
    s = skill.lower().strip()

    # replace separators
    s = re.sub(r"[\-_/]", " ", s)
    s = re.sub(r"\s+", " ", s)

    # synonym mapping
    if s in SYNONYMS:
        return SYNONYMS[s]

    return skill.strip()

STOPWORDS = {
    "company", "limited", "responsibilities", "qualification",
    "bachelor", "job", "description", "provide", "must",
    "good", "work", "office", "experience"
}

def detect_unknown_skills(text: str, known_keys: list):
    unknown = set()

    # Candidate patterns เช่น AWS Lambda, Spring Boot, Power Query
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9+/.-]{2,}(?:\s+[A-Z][A-Za-z0-9+/.-]{2,})?\b", text)

    for c in candidates:
        c_clean = c.strip()

        # Skip ถ้าอยู่ใน dict แล้ว
        if c_clean.lower() in [k.lower() for k in known_keys]:
            continue

        # Skip stopwords
        if c_clean.lower() in STOPWORDS:
            continue

        # Skip ถ้าเป็นคำทั่วไป
        if len(c_clean.split()) == 1 and c_clean.lower() in STOPWORDS:
            continue

        unknown.add(c_clean)

    return list(unknown)
