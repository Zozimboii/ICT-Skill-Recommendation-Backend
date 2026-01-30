# app/utils/advisor_rules.py
import re

INTENTS = [
    (
        "web",
        [
            "เว็บ",
            "website",
            "frontend",
            "backend",
            "fullstack",
            "เว็บแอป",
            "nuxt",
            "vue",
            "react",
        ],
    ),
    (
        "data",
        [
            "data",
            "analyst",
            "วิเคราะห์ข้อมูล",
            "data analyst",
            "bi",
            "dashboard",
            "power bi",
            "tableau",
        ],
    ),
    ("security", ["security", "cyber", "ความปลอดภัย", "แฮก", "pentest", "เครือข่าย"]),
    ("mobile", ["mobile", "แอป", "android", "ios", "flutter", "react native"]),
    ("ai", ["ai", "machine learning", "ml", "deep learning", "ปัญญาประดิษฐ์"]),
]

# ✅ ต้องมีชื่อนี้ตรง ๆ
DEFAULT_SKILLS = {
    "web": ["html", "css", "javascript", "vue", "nuxt", "node.js"],
    "data": ["sql", "excel", "python", "power bi", "tableau"],
    "security": ["networking", "linux", "python", "web basics"],
    "mobile": ["dart", "flutter", "kotlin", "swift"],
    "ai": ["python", "math", "pandas", "machine learning"],
    "general": ["python", "sql", "excel"],
}


def detect_intent(question: str) -> str:
    q = question.lower()
    for intent, keywords in INTENTS:
        if any(k.lower() in q for k in keywords):
            return intent
    return "general"


def extract_keywords(question: str):
    tokens = re.findall(r"[a-zA-Z\.\+#]{2,}", question.lower())
    return list(dict.fromkeys(tokens))  # unique preserve order
