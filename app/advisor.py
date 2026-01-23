import re

# คำหลัก → กลุ่มสายงาน
INTENTS = [
    ("web", ["เว็บ", "website", "frontend", "backend", "fullstack", "เว็บแอป", "nuxt", "vue", "react"]),
    ("data", ["data", "analyst", "วิเคราะห์ข้อมูล", "data analyst", "bi", "dashboard", "power bi", "tableau"]),
    ("security", ["security", "cyber", "ความปลอดภัย", "แฮก", "pentest", "เครือข่าย"]),
    ("mobile", ["mobile", "แอป", "android", "ios", "flutter", "react native"]),
    ("ai", ["ai", "machine learning", "ml", "deep learning", "ปัญญาประดิษฐ์"]),
]

DEFAULT_SKILLS = {
    "web": [
        "html", "css", "javascript", "vue", "nuxt", "node.js",
        "react", "typescript", "rest api", "git", "docker",
    ],
    "data": [
        "sql", "excel", "python", "power bi", "tableau",
        "pandas", "statistics", "data visualization", "etl", "data cleaning",
    ],
    "security": [
        "networking", "linux", "python", "web basics",
        "owasp top 10", "burp suite", "siem", "cryptography", "incident response",
    ],
    "mobile": [
        "dart", "flutter", "kotlin", "swift",
        "firebase", "rest api", "state management", "ui/ux", "android studio",
    ],
    "ai": [
        "python", "math", "pandas", "machine learning",
        "numpy", "scikit-learn", "deep learning", "pytorch", "model evaluation",
    ],
    "general": [
        "python", "sql", "excel",
        "git", "linux basics", "problem solving", "communication", "cloud basics",
    ],
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
