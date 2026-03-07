#skill_extractor_pro.py
import re
from app.utils.phrase_miner import extract_phrases
from app.utils.skill_dict import SKILL_DICT, SYNONYMS

STOPWORDS = {
    "company", "limited", "responsibilities",
    "qualification", "bachelor", "job",
    "description", "must", "experience"
}

def normalize_skill(skill: str):
    s = skill.lower().strip()
    s = re.sub(r"[\-_/]", " ", s)
    s = re.sub(r"\s+", " ", s)

    if s in SYNONYMS:
        return SYNONYMS[s]

    return skill.strip()


def extract_skills_pro(description: str):
    found = []
    unknown = []

    if not description:
        return found, unknown

    text = description.lower()

    # Apply synonyms
    for syn, real in SYNONYMS.items():
        text = text.replace(syn, real.lower())

    # Step 1: Known dict match
    for skill_key, skill_type in SKILL_DICT.items():
        pattern = r"(?<!\w)" + re.escape(skill_key.lower()) + r"(?!\w)"
        if re.search(pattern, text):
            found.append((skill_key, skill_type))

    # Step 2: Phrase mining unknown
    phrases = extract_phrases(text)

    for phrase in phrases:
        norm = normalize_skill(phrase)

        if norm.lower() in STOPWORDS:
            continue

        if norm not in SKILL_DICT and norm not in [x[0] for x in found]:
            unknown.append(norm)

    return found, list(set(unknown))
