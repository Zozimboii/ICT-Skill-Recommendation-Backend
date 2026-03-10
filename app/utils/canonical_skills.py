# app/utils/canonical_skills.py
"""
Single source of truth สำหรับ canonical skills
- CANONICAL_SKILLS: skills ที่ระบบยอมรับ (canonical name → skill_type)
- SKILL_ALIASES: alias → canonical name
- SKILL_BLOCKLIST: skills ที่ไม่ควรเก็บเลย
"""

# ─────────────────────────────────────────────────────────────
# CANONICAL SKILLS  (ชื่อที่ถูกต้อง → skill_type)
# ─────────────────────────────────────────────────────────────
CANONICAL_SKILLS: dict[str, str] = {

    # ── Cloud & Infrastructure ──────────────────────────────
    "AWS":              "hard_skill",
    "Azure":            "hard_skill",
    "GCP":              "hard_skill",
    "Docker":           "hard_skill",
    "Kubernetes":       "hard_skill",
    "Terraform":        "hard_skill",
    "Ansible":          "hard_skill",
    "CI/CD":            "hard_skill",
    "Jenkins":          "hard_skill",
    "GitHub Actions":   "hard_skill",
    "GitLab CI":        "hard_skill",
    "Linux":            "hard_skill",
    "Windows Server":   "hard_skill",
    "Networking":       "hard_skill",
    "TCP/IP":           "hard_skill",
    "AWS Lambda":       "hard_skill",
    "Microservices":    "hard_skill",

    # ── Programming Languages ───────────────────────────────
    "Python":           "hard_skill",
    "Java":             "hard_skill",
    "JavaScript":       "hard_skill",
    "TypeScript":       "hard_skill",
    "C#":               "hard_skill",
    "C++":              "hard_skill",
    "Go":               "hard_skill",
    "PHP":              "hard_skill",
    "Ruby":             "hard_skill",
    "Swift":            "hard_skill",
    "Kotlin":           "hard_skill",
    "Scala":            "hard_skill",
    "Rust":             "hard_skill",
    "R":                "hard_skill",
    "VBA":              "hard_skill",
    "Shell Scripting":  "hard_skill",

    # ── Web Frameworks ──────────────────────────────────────
    "React":            "hard_skill",
    "Vue":              "hard_skill",
    "Angular":          "hard_skill",
    "Node.js":          "hard_skill",
    "Django":           "hard_skill",
    "Flask":            "hard_skill",
    "FastAPI":          "hard_skill",
    "Spring Boot":      "hard_skill",
    "Laravel":          "hard_skill",
    "Next.js":          "hard_skill",
    "NestJS":           "hard_skill",
    "Express":          "hard_skill",
    "GraphQL":          "hard_skill",
    "REST API":         "hard_skill",

    # ── Frontend ────────────────────────────────────────────
    "HTML":             "hard_skill",
    "CSS":              "hard_skill",
    "Tailwind CSS":     "hard_skill",
    "SASS":             "hard_skill",

    # ── Database ────────────────────────────────────────────
    "SQL":              "hard_skill",
    "MySQL":            "hard_skill",
    "PostgreSQL":       "hard_skill",
    "MongoDB":          "hard_skill",
    "Redis":            "hard_skill",
    "Oracle":           "hard_skill",
    "Elasticsearch":    "hard_skill",

    # ── Data & Analytics ────────────────────────────────────
    "Machine Learning": "hard_skill",
    "Deep Learning":    "hard_skill",
    "NLP":              "hard_skill",
    "Data Science":     "hard_skill",
    "Data Analytics":   "hard_skill",
    "TensorFlow":       "hard_skill",
    "PyTorch":          "hard_skill",
    "Pandas":           "hard_skill",
    "NumPy":            "hard_skill",
    "Spark":            "hard_skill",
    "Power BI":         "hard_skill",
    "Tableau":          "hard_skill",
    "Excel":            "hard_skill",
    "Data Visualization": "hard_skill",
    "Data Modeling":    "hard_skill",
    "ETL":              "hard_skill",
    "Data Governance":  "hard_skill",

    # ── AI / LLM ────────────────────────────────────────────
    "LLM":              "hard_skill",
    "OpenAI API":       "hard_skill",

    # ── Security ────────────────────────────────────────────
    "Cybersecurity":        "hard_skill",
    "Penetration Testing":  "hard_skill",
    "Network Security":     "hard_skill",
    "Application Security": "hard_skill",
    "SOC":                  "hard_skill",
    "SIEM":                 "hard_skill",
    "ISO 27001":            "hard_skill",
    "OWASP":                "hard_skill",
    "Vulnerability Assessment": "hard_skill",
    "Incident Response":    "hard_skill",

    # ── Dev Practices ───────────────────────────────────────
    "Git":              "hard_skill",
    "Agile":            "hard_skill",
    "Scrum":            "hard_skill",
    "Unit Testing":     "hard_skill",
    "Automation Testing": "hard_skill",
    "QA":               "hard_skill",
    "Code Review":      "hard_skill",
    "System Design":    "hard_skill",
    "System Architecture": "hard_skill",

    # ── Business / Analysis ─────────────────────────────────
    "Business Analysis":    "hard_skill",
    "System Analysis":      "hard_skill",
    "Requirements Gathering": "hard_skill",
    "ERP":                  "hard_skill",
    "CRM":                  "hard_skill",
    "Product Management":   "hard_skill",
    "Project Management":   "hard_skill",
    "Risk Management":      "hard_skill",
    "Change Management":    "hard_skill",
    "Digital Transformation": "hard_skill",

    # ── Design & UX ─────────────────────────────────────────
    "UX Design":        "hard_skill",
    "UI Design":        "hard_skill",
    "Figma":            "hard_skill",
    "Prototyping":      "hard_skill",

    # ── Soft Skills ─────────────────────────────────────────
    "Communication":        "soft_skill",
    "Teamwork":             "soft_skill",
    "Leadership":           "soft_skill",
    "Problem Solving":      "soft_skill",
    "Critical Thinking":    "soft_skill",
    "Time Management":      "soft_skill",
    "Adaptability":         "soft_skill",
    "Collaboration":        "soft_skill",
    "Creativity":           "soft_skill",
    "Stakeholder Management": "soft_skill",
    "Strategic Thinking":   "soft_skill",
    "Negotiation":          "soft_skill",
    "Mentoring":            "soft_skill",
    "Presentation Skills":  "soft_skill",
    "Analytical Thinking":  "soft_skill",
    "Attention to Detail":  "soft_skill",
    "Coaching":             "soft_skill",
    "Emotional Intelligence": "soft_skill",
    "Team Leadership":      "soft_skill",
}

# ─────────────────────────────────────────────────────────────
# ALIASES  (lowercase alias → canonical name)
# ─────────────────────────────────────────────────────────────
SKILL_ALIASES: dict[str, str] = {

    # Cloud
    "amazon web services":      "AWS",
    "aws cloud":                "AWS",
    "microsoft azure":          "Azure",
    "google cloud":             "GCP",
    "google cloud platform":    "GCP",
    "cloud technology":         "AWS",           # generic → AWS (most common)
    "cloud technologies":       "AWS",
    "aws lambda":               "AWS Lambda",

    # Containers
    "k8s":                      "Kubernetes",
    "docker container":         "Docker",

    # CI/CD
    "cicd":                     "CI/CD",
    "ci cd":                    "CI/CD",
    "github actions":           "GitHub Actions",
    "gitlab ci":                "GitLab CI",

    # Languages
    "c sharp":                  "C#",
    "dotnet":                   "C#",
    ".net":                     "C#",
    "golang":                   "Go",
    "nodejs":                   "Node.js",
    "node js":                  "Node.js",
    "r programming":            "R",
    "visual c+":                "C++",
    "shell script":             "Shell Scripting",
    "bash":                     "Shell Scripting",

    # Web
    "reactjs":                  "React",
    "react.js":                 "React",
    "vuejs":                    "Vue",
    "vue.js":                   "Vue",
    "angularjs":                "Angular",
    "angular js":               "Angular",
    "nextjs":                   "Next.js",
    "nestjs":                   "NestJS",
    "spring":                   "Spring Boot",
    "express.js":               "Express",
    "expressjs":                "Express",
    "wpf framework":            "C#",
    "html5":                    "HTML",
    "css3":                     "CSS",
    "sass":                     "SASS",
    "less":                     "CSS",
    "tailwind":                 "Tailwind CSS",

    # Database
    "postgresql":               "PostgreSQL",
    "postgres":                 "PostgreSQL",
    "microsoft sql server":     "SQL",
    "mysql server":             "MySQL",
    "nosql":                    "MongoDB",
    "rdbms":                    "SQL",
    "databases":                "SQL",

    # Data
    "data analysis":            "Data Analytics",
    "data analytics":           "Data Analytics",
    "data synthesis":           "Data Analytics",
    "insight generation":       "Data Analytics",
    "data-driven":              "Data Analytics",
    "analytical skills":        "Analytical Thinking",
    "powerbi":                  "Power BI",
    "power query":              "Excel",
    "pivot table":              "Excel",
    "vlookup":                  "Excel",
    "microsoft excel":          "Excel",
    "pyspark":                  "Spark",
    "sas viya":                 "Data Analytics",
    "spc":                      "Data Analytics",
    "regression analysis":      "Data Modeling",
    "forecasting":              "Data Analytics",
    "data collection systems":  "Data Analytics",

    # AI/ML
    "artificial intelligence":  "LLM",
    "ai":                       "LLM",
    "ai technologies":          "LLM",
    "llms":                     "LLM",
    "peft":                     "LLM",
    "openai":                   "OpenAI API",

    # Security
    "cybersecurity":            "Cybersecurity",
    "information security":     "Cybersecurity",
    "it infrastructure security": "Network Security",
    "ot network security":      "Network Security",
    "penetration testing (pentest)": "Penetration Testing",
    "pentest":                  "Penetration Testing",
    "vulnerability assessment (va)": "Vulnerability Assessment",
    "sast":                     "Application Security",
    "dast":                     "Application Security",
    "static application security testing": "Application Security",
    "dynamic application security testing": "Application Security",
    "owasp":                    "OWASP",
    "xss (security)":           "OWASP",
    "csrf (security)":          "OWASP",
    "injection (security)":     "OWASP",
    "iso27001":                 "ISO 27001",
    "security incident response": "Incident Response",
    "incident response planning": "Incident Response",

    # Dev practices
    "tdd":                      "Unit Testing",
    "jest":                     "Unit Testing",
    "selenium":                 "Automation Testing",
    "quality assurance":        "QA",
    "swagger":                  "REST API",
    "websocket":                "REST API",
    "microservice":             "Microservices",
    "design patterns":          "System Design",
    "solution design":          "System Design",
    "system architecture":      "System Architecture",
    "technical specification":  "System Design",

    # Business
    "business analyst":         "Business Analysis",
    "business process analysis": "Business Analysis",
    "business process design":  "Business Analysis",
    "process reengineering":    "Business Analysis",
    "requirements elicitation": "Requirements Gathering",
    "requirement analysis":     "Requirements Gathering",
    "user story writing":       "Requirements Gathering",
    "functional specification writing": "Requirements Gathering",
    "uat facilitation":         "QA",
    "system analyst":           "System Analysis",
    "system testing":           "QA",
    "erp systems":              "ERP",
    "erp software":             "ERP",
    "erp software development": "ERP",
    "microsoft dynamics":       "ERP",
    "dynamics erp":             "ERP",
    "crm systems":              "CRM",
    "digital transformation":   "Digital Transformation",
    "digital value creation":   "Digital Transformation",
    "digital solution development": "Digital Transformation",
    "digital solutions":        "Digital Transformation",
    "product development":      "Product Management",
    "release management":       "Project Management",
    "project implementation":   "Project Management",
    "process improvement":      "Change Management",
    "change management":        "Change Management",
    "risk analysis":            "Risk Management",
    "it audit":                 "Risk Management",

    # UX/Design
    "ux":                       "UX Design",
    "ui":                       "UI Design",
    "ui/ux":                    "UX Design",
    "user research":            "UX Design",
    "website design":           "UI Design",
    "figma":                    "Figma",

    # Soft skills
    "communication (english)":  "Communication",
    "communication (thai)":     "Communication",
    "english communication":    "Communication",
    "written communication":    "Communication",
    "verbal communication":     "Communication",
    "interpersonal skills":     "Communication",
    "active listening":         "Communication",
    "facilitation":             "Communication",
    "team management":          "Team Leadership",
    "team coordination":        "Team Leadership",
    "team leadership":          "Team Leadership",
    "coaching":                 "Coaching",
    "mentoring":                "Mentoring",
    "analytical thinking":      "Analytical Thinking",
    "detail-oriented":          "Attention to Detail",
    "accuracy":                 "Attention to Detail",
    "customer-centric mindset": "Emotional Intelligence",
    "empathy":                  "Emotional Intelligence",
    "stress management":        "Adaptability",
    "resilience":               "Adaptability",
    "quick learning":           "Adaptability",
    "continuous learning":      "Adaptability",
    "continuous improvement":   "Adaptability",
    "coordination":             "Collaboration",
    "planning":                 "Project Management",
    "scheduling":               "Project Management",
    "proactiveness":            "Adaptability",
}

# ─────────────────────────────────────────────────────────────
# BLOCKLIST  (ไม่เก็บเลย)
# ─────────────────────────────────────────────────────────────
SKILL_BLOCKLIST: set[str] = {
    # ภาษา / certifications ที่ไม่ใช่ skill จริง
    "english", "thai", "thai (native)", "english (good command)",
    "english language proficiency", "thai language proficiency",
    "chinese language proficiency", "english proficiency",
    "jlpt n2",

    # แพลตฟอร์ม social media
    "youtube platform knowledge", "youtube marketing",
    "tiktok marketing", "meta marketing",
    "instagram platform knowledge", "facebook platform knowledge",
    "google platform knowledge",

    # Build tools ที่ไม่ใช่ skill หลัก
    "yarn", "webpack", "babel", "vite", "npm", "swc",

    # industry knowledge (vague มาก)
    "energy industry knowledge", "retail industry knowledge",
    "lifestyle ecosystem knowledge", "platform economy",
    "financial domain knowledge", "insurance domain knowledge",

    # insurance-specific
    "policy (insurance)", "underwriting (insurance)",
    "claims (insurance)", "billing (insurance)",

    # ภาษา/tools เฉพาะทาง
    "scada", "historians",
    "design of experiments (doe)", "a-b testing",

    # generic noise
    "computer literacy", "professionalism",
    "confidentiality", "discretion",
    "responsibility", "proactiveness",
    "programming",   # generic เกินไป

    # DC-specific
    "data center operations", "dc capacity management",
    "server management", "router management",
    "switch management", "equipment operation",

    # IT support (granular เกิน)
    "hardware support", "software support",
    "application installation", "it asset management",
    "system installation", "system configuration",
    "operating system support", "windows operating system",
    "macos operating system",

    # certifications ที่ควรเป็น separate field
    "cisa",

    # jira/confluence = tools ไม่ใช่ skill
    "jira", "confluence",

    # ไม่ชัดเจน
    "nist", "gdpr", "it security regulations",
    "compliance management", "compliance",
    "monitoring", "alerting", "logging",
    "troubleshooting", "error handling",
    "bug fixing", "debugging",
    "documentation", "report writing",
    "training", "customer support",
    "technical support",
    "web banking solutions", "mobile banking solutions",
    "market research", "competitor analysis",
    "cost/benefit analysis", "software selection",
    "data lineage", "data dictionary", "access controls",
    "data recording systems",
    "security reporting", "security policy development",
    "security policy implementation",
    "security awareness training",
    "security incident monitoring",
    "security incident analysis",
    "security solution assessment",
    "security technology evaluation",
    "pc security", "server security",
    "incident identification", "incident containment",
    "incident eradication", "incident response lifecycle management",
    "translating data insights into action",
    "data literacy",
}


def normalize_skill(raw: str) -> str | None:
    """
    raw skill name → canonical name หรือ None ถ้าควร block

    Steps:
    1. lowercase + strip
    2. check blocklist
    3. check alias → canonical
    4. check if already canonical
    5. return None (ไม่รู้จัก)
    """
    cleaned = raw.strip().lower()

    # 1. blocklist
    if cleaned in SKILL_BLOCKLIST or raw.strip().lower() in {b.lower() for b in SKILL_BLOCKLIST}:
        return None

    # 2. alias lookup
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]

    # 3. already canonical (case-insensitive check)
    canonical_lower = {k.lower(): k for k in CANONICAL_SKILLS}
    if cleaned in canonical_lower:
        return canonical_lower[cleaned]

    # 4. partial match สำหรับ alias
    for alias, canonical in SKILL_ALIASES.items():
        if alias in cleaned or cleaned in alias:
            return canonical

    return None  # ไม่รู้จัก → ไม่เก็บ