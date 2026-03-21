# app/utils/course_skill_map.py
# Map ชื่อวิชา (keyword) → skills ที่น่าจะได้จากวิชานั้น
# skill names ต้องตรงกับ Skill.name ใน DB (case-sensitive)

COURSE_SKILL_MAP: list[tuple[str, list[str]]] = [

    # ════════════════════════════════════════════════════════════
    # ENGLISH KEYWORDS
    # ════════════════════════════════════════════════════════════

    # ── Programming ──────────────────────────────────────────────
    ("computer programming",        ["python", "problem solving"]),
    ("programming fundamentals",    ["python", "problem solving"]),
    ("introduction to programming", ["python", "problem solving"]),
    ("object oriented",             ["python", "design patterns", "problem solving"]),
    ("data structures",             ["python", "problem solving"]),
    ("algorithm",                   ["python", "problem solving"]),
    ("discrete mathematics",        ["problem solving", "analytical thinking"]),
    ("calculus",                    ["analytical thinking"]),
    ("linear algebra",              ["python", "analytical thinking"]),
    ("numerical method",            ["python", "analytical thinking"]),

    # ── Software Engineering ─────────────────────────────────────
    ("software engineering",        ["git", "agile development", "problem solving"]),
    ("software development",        ["git", "agile development", "system development"]),
    ("software design",             ["design patterns", "git"]),
    ("software testing",            ["unit testing", "tdd", "quality assurance"]),
    ("software quality",            ["quality assurance", "tdd"]),
    ("software project",            ["project management", "agile project management"]),
    ("software process",            ["agile development", "process improvement"]),
    ("software architecture",       ["design patterns", "enterprise architecture"]),
    ("software maintenance",        ["git", "system development"]),
    ("software metrics",            ["quality assurance", "analytical skills"]),
    ("agile",                       ["agile development", "agile project management", "collaboration"]),
    ("scrum",                       ["agile project management", "agile development"]),

    # ── Web ──────────────────────────────────────────────────────
    ("web programming",             ["html", "css", "javascript"]),
    ("web development",             ["html", "css", "javascript", "react", "node.js"]),
    ("web application",             ["html", "css", "javascript", "web application development"]),
    ("internet programming",        ["html", "css", "javascript"]),
    ("web design",                  ["html", "css", "ui/ux"]),
    ("web service",                 ["javascript", "node.js", "system integration"]),
    ("web technology",              ["html", "css", "javascript"]),
    ("front end",                   ["html", "css", "javascript", "react", "vue", "angular"]),
    ("frontend",                    ["html", "css", "javascript", "react", "vue"]),
    ("back end",                    ["node.js", "express", "sql", "system development"]),
    ("backend",                     ["node.js", "express", "sql"]),
    ("full stack",                  ["html", "css", "javascript", "node.js", "full stack development"]),

    # ── Database ─────────────────────────────────────────────────
    ("database",                    ["sql", "database systems", "query language"]),
    ("data management",             ["sql", "data management frameworks", "database"]),
    ("data warehouse",              ["sql", "data architecture", "data integration"]),
    ("database design",             ["sql", "database systems", "data architecture"]),
    ("database administration",     ["sql", "database systems", "data governance"]),

    # ── Network ──────────────────────────────────────────────────
    ("computer network",            ["networking", "system integration"]),
    ("network programming",         ["networking", "python"]),
    ("network security",            ["cybersecurity", "compliance"]),
    ("information security",        ["cybersecurity", "compliance", "data privacy"]),
    ("cyber",                       ["cybersecurity", "compliance"]),
    ("network administration",      ["networking", "linux"]),

    # ── OS / System ──────────────────────────────────────────────
    ("operating system",            ["linux", "system development"]),
    ("system programming",          ["linux", "c++"]),
    ("computer architecture",       ["linux", "system development"]),
    ("embedded system",             ["c++", "iot"]),
    ("microcontroller",             ["c++", "iot"]),
    ("iot",                         ["iot", "c++", "python"]),
    ("internet of things",          ["iot", "python"]),

    # ── AI / Data Science ────────────────────────────────────────
    ("machine learning",            ["python", "machine learning", "data analysis", "analytical thinking"]),
    ("artificial intelligence",     ["python", "ai", "machine learning"]),
    ("deep learning",               ["python", "ai", "data analysis"]),
    ("data science",                ["python", "data analysis", "data analytics", "data visualization"]),
    ("data mining",                 ["python", "machine learning", "sql", "data analysis"]),
    ("data analytics",              ["python", "data analytics", "data analysis", "data visualization"]),
    ("data analysis",               ["python", "data analysis", "sql", "analytical thinking"]),
    ("business intelligence",       ["business intelligence", "power bi", "bi tools", "data visualization"]),
    ("natural language",            ["python", "ai", "llm"]),
    ("computer vision",             ["python", "ai"]),
    ("statistics",                  ["python", "data analysis", "analytical skills"]),
    ("statistical",                 ["python", "analytical thinking"]),
    ("probability",                 ["python", "analytical thinking"]),
    ("data visualization",          ["data visualization", "power bi", "bi tools"]),
    ("predictive",                  ["machine learning", "data analysis", "python"]),

    # ── Mobile ───────────────────────────────────────────────────
    ("mobile application",          ["javascript", "react native"]),
    ("mobile development",          ["javascript", "react native"]),
    ("android",                     ["java", "kotlin"]),
    ("ios",                         ["swift"]),

    # ── Cloud / DevOps ───────────────────────────────────────────
    ("cloud computing",             ["cloud", "aws", "azure", "docker"]),
    ("cloud technology",            ["cloud technology", "aws", "azure", "cloud platform engineering"]),
    ("devops",                      ["docker", "git", "ci/cd"]),
    ("containerization",            ["docker", "kubernetes"]),
    ("cloud native",                ["docker", "aws", "azure", "cloud platform engineering"]),
    ("infrastructure",              ["docker", "cloud", "linux"]),

    # ── Business Analysis / ERP ───────────────────────────────────
    ("business analysis",           ["business analysis", "requirements gathering", "requirements documentation"]),
    ("system analysis",             ["business analysis", "analytical thinking", "requirements gathering"]),
    ("requirement",                 ["requirements gathering", "requirements documentation", "problem solving"]),
    ("business process",            ["business process development", "process improvement", "workflow analysis"]),
    ("erp",                         ["erp", "system integration", "business process development"]),
    ("crm",                         ["crm", "business analysis"]),
    ("enterprise resource",         ["erp", "enterprise architecture"]),
    ("digital transformation",      ["digital transformation", "change management", "cloud technology"]),

    # ── Project / Process Management ─────────────────────────────
    ("project management",          ["project management", "agile project management", "planning"]),
    ("software project",            ["project management", "agile project management"]),
    ("quality assurance",           ["quality assurance", "tdd", "unit testing"]),
    ("quality management",          ["quality assurance", "process improvement", "compliance management"]),
    ("process management",          ["process improvement", "process reengineering", "workflow analysis"]),
    ("risk management",             ["risk assessment", "compliance management", "planning"]),
    ("change management",           ["change management", "stakeholder management", "communication"]),

    # ── Testing ───────────────────────────────────────────────────
    ("testing",                     ["unit testing", "tdd", "quality assurance", "test case creation"]),
    ("test",                        ["unit testing", "test case creation", "test execution"]),
    ("acceptance test",             ["user acceptance testing (uat)", "quality assurance"]),

    # ── Soft Skills ───────────────────────────────────────────────
    ("communication",               ["communication", "presentation skills"]),
    ("presentation",                ["presentation skills", "communication"]),
    ("teamwork",                    ["collaboration", "team management", "coordination"]),
    ("leadership",                  ["leadership", "team management"]),
    ("internship",                  ["collaboration", "communication", "problem solving"]),
    ("cooperative education",       ["collaboration", "communication", "adaptability"]),
    ("senior project",              ["project management", "collaboration", "problem solving"]),
    ("capstone",                    ["project management", "collaboration"]),
    ("professional",                ["communication", "english proficiency", "adaptability"]),
    ("english",                     ["english proficiency", "communication"]),

    # ── Finance / Business ────────────────────────────────────────
    ("accounting",                  ["microsoft excel", "data analysis", "compliance"]),
    ("finance",                     ["microsoft excel", "data analysis", "fintech"]),
    ("marketing",                   ["data analysis", "marketing data analysis", "crm"]),
    ("e-commerce",                  ["digital transformation", "crm", "data analytics"]),
    ("business intelligence",       ["business intelligence", "power bi", "data visualization"]),
    ("strategic",                   ["strategic thinking", "analytical thinking", "planning"]),

    # ════════════════════════════════════════════════════════════
    # THAI KEYWORDS
    # ════════════════════════════════════════════════════════════

    # ── Programming ──────────────────────────────────────────────
    ("การโปรแกรม",                  ["python", "problem solving"]),
    ("โปรแกรมมิ่ง",                 ["python", "problem solving"]),
    ("โครงสร้างข้อมูล",             ["python", "problem solving"]),
    ("ขั้นตอนวิธี",                 ["python", "problem solving", "analytical thinking"]),
    ("อัลกอริทึม",                  ["python", "problem solving"]),
    ("การเขียนโปรแกรม",             ["python", "problem solving"]),
    ("ภาษาโปรแกรม",                 ["python", "problem solving"]),
    ("วิศวกรรมซอฟต์แวร์",           ["git", "agile development", "system development"]),
    ("การพัฒนาซอฟต์แวร์",           ["git", "agile development"]),

    # ── Web ──────────────────────────────────────────────────────
    ("การพัฒนาเว็บ",                ["html", "css", "javascript"]),
    ("เว็บแอปพลิเคชัน",             ["html", "css", "javascript", "web application development"]),
    ("เว็บโปรแกรมมิ่ง",             ["html", "css", "javascript"]),

    # ── Database ─────────────────────────────────────────────────
    ("ฐานข้อมูล",                   ["sql", "database systems", "query language"]),
    ("การจัดการข้อมูล",              ["sql", "data management frameworks"]),
    ("คลังข้อมูล",                  ["sql", "data architecture", "data warehouse"]),

    # ── Network ──────────────────────────────────────────────────
    ("เครือข่าย",                   ["networking", "system integration"]),
    ("เครือข่ายคอมพิวเตอร์",         ["networking"]),
    ("ความมั่นคง",                  ["cybersecurity", "compliance"]),
    ("ความปลอดภัย",                  ["cybersecurity", "data privacy"]),

    # ── AI / Data Science ────────────────────────────────────────
    ("ปัญญาประดิษฐ์",               ["python", "ai", "machine learning"]),
    ("การเรียนรู้ของเครื่อง",        ["python", "machine learning", "data analysis"]),
    ("วิทยาการข้อมูล",               ["python", "data science", "data analytics"]),
    ("การวิเคราะห์ข้อมูล",           ["python", "data analysis", "sql", "analytical thinking"]),
    ("เหมืองข้อมูล",                ["python", "machine learning", "data analysis"]),
    ("การประมวลผลภาษา",              ["python", "ai", "llm"]),
    ("สถิติ",                       ["python", "data analysis", "analytical thinking"]),
    ("วิธีเชิงตัวเลข",               ["python", "analytical thinking"]),

    # ── Cloud / DevOps ───────────────────────────────────────────
    ("คลาวด์",                      ["cloud", "aws", "azure"]),
    ("การประมวลผลแบบคลาวด์",        ["cloud technology", "aws", "azure"]),

    # ── System / OS ──────────────────────────────────────────────
    ("ระบบปฏิบัติการ",              ["linux", "system development"]),
    ("สถาปัตยกรรมคอมพิวเตอร์",      ["linux", "system development"]),
    ("ระบบฝังตัว",                  ["c++", "iot"]),
    ("อินเทอร์เน็ตของสรรพสิ่ง",     ["iot", "python"]),

    # ── Mobile ───────────────────────────────────────────────────
    ("แอปพลิเคชันมือถือ",            ["javascript", "react native"]),
    ("การพัฒนาแอป",                 ["javascript", "react native"]),

    # ── Business / Management ────────────────────────────────────
    ("การวิเคราะห์ธุรกิจ",           ["business analysis", "requirements gathering", "analytical thinking"]),
    ("การจัดการโครงการ",             ["project management", "agile project management", "planning"]),
    ("การบริหารโครงการ",             ["project management", "planning", "leadership"]),
    ("กระบวนการทางธุรกิจ",          ["business process development", "process improvement"]),
    ("การจัดการการเปลี่ยนแปลง",      ["change management", "stakeholder management"]),
    ("การประกันคุณภาพ",              ["quality assurance", "tdd"]),
    ("การทดสอบซอฟต์แวร์",           ["unit testing", "test case creation", "quality assurance"]),

    # ── Soft Skills ──────────────────────────────────────────────
    ("การสื่อสาร",                  ["communication", "presentation skills"]),
    ("ภาวะผู้นำ",                   ["leadership", "team management"]),
    ("การทำงานเป็นทีม",              ["collaboration", "team management", "coordination"]),
    ("โครงงาน",                     ["project management", "collaboration", "problem solving"]),
    ("สหกิจ",                       ["collaboration", "communication", "adaptability"]),
    ("ฝึกงาน",                      ["collaboration", "communication", "adaptability"]),
    ("ภาษาอังกฤษ",                  ["english proficiency", "communication"]),
    ("การนำเสนอ",                   ["presentation skills", "communication"]),
    ("ความคิดสร้างสรรค์",            ["innovation", "analytical thinking"]),
    ("การคิดเชิงวิเคราะห์",          ["analytical thinking", "analytical skills", "problem solving"]),
    ("การแก้ปัญหา",                 ["problem solving", "analytical thinking"]),

    # ── Finance / Accounting ─────────────────────────────────────
    ("การบัญชี",                    ["microsoft excel", "data analysis", "compliance"]),
    ("การเงิน",                     ["microsoft excel", "data analysis", "fintech"]),
    ("การตลาด",                     ["marketing data analysis", "crm", "data analytics"]),
    ("พาณิชย์อิเล็กทรอนิกส์",       ["digital transformation", "crm"]),
]

COURSE_SKILL_MAP_ADDITIONS = [
    ("fastapi",      ["FastAPI", "python", "REST API"]),
    ("django",       ["Django", "python", "sql"]),
    ("flask",        ["Flask", "python", "REST API"]),
    ("pytorch",      ["PyTorch", "python", "machine learning"]),
    ("tensorflow",   ["TensorFlow", "python", "machine learning"]),
    ("scikit",       ["Scikit-learn", "python", "machine learning"]),
    ("spark",        ["Apache Spark", "python", "data analytics"]),
    ("hadoop",       ["Hadoop", "data analytics"]),
    ("kafka",        ["Kafka", "data integration"]),
    ("kubernetes",   ["Kubernetes", "docker"]),
    ("terraform",    ["Terraform", "cloud platform engineering"]),
    ("graphql",      ["GraphQL", "javascript"]),
    ("microservice", ["Microservices", "docker", "REST API"]),
    ("rest api",     ["REST API", "system integration"]),
    ("การเรียนรู้เชิงลึก", ["PyTorch", "TensorFlow", "python"]),
    ("การประมวลผลแบบกลุ่ม", ["Apache Spark", "Hadoop"]),
]
