# scripts/review_unknown_skills.py
# กรอง unknown_skills.txt และเพิ่มเข้า skill_dict.py แบบ semi-automatic
#
# Usage:
#   py -m scripts.review_unknown_skills              ← interactive mode
#   py -m scripts.review_unknown_skills --auto       ← เพิ่มเฉพาะที่ผ่าน filter อัตโนมัติ

import re
import sys
from pathlib import Path

UNKNOWN_FILE    = Path("unknown_skills.txt")
SKILL_DICT_FILE = Path("app/utils/skill_dict.py")

# check original case
CASE_SENSITIVE_PATTERNS = [
    r"^\d",
    r"^\d+\s+\w+$",
    r"^[a-z]",
    r"^.{1,2}$",
    r"^.{50,}$",
    r"(.)\1{3,}",
    r"[&%$#@!(){}\[\]]",
]

# check lowercase
CASE_INSENSITIVE_PATTERNS = [
    r"\d{3,}",
    r"^(job|qualifications?|responsibilities?|requirements?|description|summary|about|us|at|for|the|our|we|you|your|key|must|have|good|strong|work|provide|ensure|support|manage|develop|team|with|this|that|will|can|able|or|and|in|of|to|a|an|is|are|be|been|has|had|was|were)$",
    r"^(job|key|work|team|company|business|role|please|thank|note|contact)\s+\w+$",
    r"\b(bachelor|master|degree|university|college|school|graduate|intern|candidate|applicant)\b",
    r"\b(limited|company|corporation|thailand|bangkok|office|tower|road|street|floor|building|mrt|bts|station)\b",
    r"\b(please|contact|apply|send|email|tel|phone|fax|resume|cv|salary|benefit|bonus|insurance)\b",
    r"\b(years?|months?|days?|weeks?|hours?)\s*(of|experience|ago|old)\b",
    r"\b(minimum|maximum|least|most|more|less|over|under|above|below)\b",
]

WHITELIST = {
    "C++", "C#", ".NET", "Node.js", "Vue.js", "React.js",
    "CI/CD", "REST API", "GraphQL", "TypeScript", "NestJS",
}

HARD_SKILL_HINTS = [
    "js", "css", "sql", "api", "sdk", "cli", "ui", "ux",
    "aws", "gcp", "ci", "cd", "ml", "ai", "nlp", "etl",
    "react", "vue", "node", "django", "flask", "spring",
    "docker", "k8s", "terraform", "ansible",
    "python", "java", "kotlin", "swift", "rust", "go",
    "postgres", "mysql", "redis", "mongo",
    "tensorflow", "pytorch", "scikit",
]

SOFT_SKILL_HINTS = [
    "communication", "leadership", "teamwork", "management",
    "collaboration", "problem", "critical", "analytical",
    "presentation", "negotiation", "mentoring",
]


def is_noise(text: str) -> bool:
    if text in WHITELIST:
        return False
    for pattern in CASE_SENSITIVE_PATTERNS:
        if re.search(pattern, text):
            return True
    text_lower = text.lower()
    for pattern in CASE_INSENSITIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def guess_skill_type(text: str) -> str:
    text_lower = text.lower()
    if any(h in text_lower for h in SOFT_SKILL_HINTS):
        return "soft_skill"
    return "hard_skill"


def load_existing_skills() -> set:
    content = SKILL_DICT_FILE.read_text(encoding="utf-8")
    return set(re.findall(r'"([^"]+)":\s*"(?:hard|soft)_skill"', content))


def append_to_skill_dict(skills):
    if not skills:
        return
    content = SKILL_DICT_FILE.read_text(encoding="utf-8")
    new_lines = "\n    # --- Auto-added from unknown_skills review ---\n"
    for name, skill_type in skills:
        new_lines += f'    "{name}": "{skill_type}",\n'
    content = content.rstrip()
    if content.endswith("})"):
        content = content[:-2] + new_lines + "})\n"
    else:
        content += new_lines
    SKILL_DICT_FILE.write_text(content, encoding="utf-8")
    print(f"\n✅ เพิ่ม {len(skills)} skills เข้า skill_dict.py แล้ว")


def main():
    auto_mode = "--auto" in sys.argv

    if not UNKNOWN_FILE.exists():
        print("❌ ไม่พบ unknown_skills.txt")
        return

    raw        = UNKNOWN_FILE.read_text(encoding="utf-8").splitlines()
    candidates = sorted({line.strip() for line in raw if line.strip()})
    existing   = load_existing_skills()
    filtered   = [c for c in candidates if not is_noise(c) and c not in existing]

    print(f"📋 unknown skills ทั้งหมด : {len(candidates)}")
    print(f"🔍 ผ่าน filter           : {len(filtered)}")
    print(f"📚 มีใน dict แล้ว / noise: {len(candidates) - len(filtered)}\n")

    if not filtered:
        print("✅ ไม่มี skill ใหม่ที่ต้องเพิ่ม")
        return

    to_add = []

    if auto_mode:
        for skill in filtered:
            skill_type = guess_skill_type(skill)
            to_add.append((skill, skill_type))
            print(f"  ✅ {skill} [{skill_type}]")
    else:
        print("กด y=เพิ่ม  n=ข้าม  h=hard_skill  s=soft_skill  q=ออก\n")
        for skill in filtered:
            guessed = guess_skill_type(skill)
            ans = input(f"[{guessed}] {skill}? (y/n/h/s/q): ").strip().lower()
            if ans == "q":
                break
            elif ans in ("y", ""):
                to_add.append((skill, guessed))
            elif ans == "h":
                to_add.append((skill, "hard_skill"))
            elif ans == "s":
                to_add.append((skill, "soft_skill"))

    append_to_skill_dict(to_add)
    UNKNOWN_FILE.write_text("", encoding="utf-8")
    print("🧹 ล้าง unknown_skills.txt แล้ว")


if __name__ == "__main__":
    main()