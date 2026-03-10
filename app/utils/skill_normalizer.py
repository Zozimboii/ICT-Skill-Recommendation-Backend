# app/utils/skill_normalizer.py
"""
Unified Skill Normalization
ใช้แทน skill_dict.py + canonical_skills.py

Flow:
  raw_name → normalize() → canonical_name | None (blocked)

normalize() ทำงานแบบนี้:
  1. lowercase + strip
  2. check blocklist → None
  3. check ALIASES → canonical_name
  4. check CANONICAL_SKILLS (exact, case-insensitive) → canonical_name
  5. partial match → canonical_name
  6. None (ไม่รู้จัก → ไม่เก็บ)
"""

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL SKILLS  (ชื่อ display ที่ถูกต้อง → skill_type)
# ─────────────────────────────────────────────────────────────────────────────
CANONICAL_SKILLS: dict[str, str] = {

    # Cloud & Infrastructure
    "AWS":                  "hard_skill",
    "Azure":                "hard_skill",
    "GCP":                  "hard_skill",
    "Docker":               "hard_skill",
    "Kubernetes":           "hard_skill",
    "Terraform":            "hard_skill",
    "Ansible":              "hard_skill",
    "CI/CD":                "hard_skill",
    "Jenkins":              "hard_skill",
    "GitHub Actions":       "hard_skill",
    "GitLab CI":            "hard_skill",
    "Linux":                "hard_skill",
    "Windows Server":       "hard_skill",
    "Networking":           "hard_skill",
    "TCP/IP":               "hard_skill",
    "AWS Lambda":           "hard_skill",
    "Microservices":        "hard_skill",

    # Programming Languages
    "Python":               "hard_skill",
    "Java":                 "hard_skill",
    "JavaScript":           "hard_skill",
    "TypeScript":           "hard_skill",
    "C#":                   "hard_skill",
    "C++":                  "hard_skill",
    "Go":                   "hard_skill",
    "PHP":                  "hard_skill",
    "Ruby":                 "hard_skill",
    "Swift":                "hard_skill",
    "Kotlin":               "hard_skill",
    "Scala":                "hard_skill",
    "Rust":                 "hard_skill",
    "R":                    "hard_skill",
    "VBA":                  "hard_skill",
    "Shell Scripting":      "hard_skill",

    # Web Frameworks
    "React":                "hard_skill",
    "Vue":                  "hard_skill",
    "Angular":              "hard_skill",
    "Node.js":              "hard_skill",
    "Django":               "hard_skill",
    "Flask":                "hard_skill",
    "FastAPI":              "hard_skill",
    "Spring Boot":          "hard_skill",
    "Laravel":              "hard_skill",
    "Next.js":              "hard_skill",
    "NestJS":               "hard_skill",
    "Express":              "hard_skill",
    "GraphQL":              "hard_skill",
    "REST API":             "hard_skill",
    "React Native":         "hard_skill",

    # Frontend
    "HTML":                 "hard_skill",
    "CSS":                  "hard_skill",
    "Tailwind CSS":         "hard_skill",
    "SASS":                 "hard_skill",

    # Database
    "SQL":                  "hard_skill",
    "MySQL":                "hard_skill",
    "PostgreSQL":           "hard_skill",
    "MongoDB":              "hard_skill",
    "Redis":                "hard_skill",
    "Oracle":               "hard_skill",
    "Elasticsearch":        "hard_skill",

    # Data & Analytics
    "Machine Learning":     "hard_skill",
    "Deep Learning":        "hard_skill",
    "NLP":                  "hard_skill",
    "Data Science":         "hard_skill",
    "Data Analytics":       "hard_skill",
    "TensorFlow":           "hard_skill",
    "PyTorch":              "hard_skill",
    "Pandas":               "hard_skill",
    "NumPy":                "hard_skill",
    "Spark":                "hard_skill",
    "Hadoop":               "hard_skill",
    "Airflow":              "hard_skill",
    "Kafka":                "hard_skill",
    "Power BI":             "hard_skill",
    "Tableau":              "hard_skill",
    "Excel":                "hard_skill",
    "Data Visualization":   "hard_skill",
    "Data Modeling":        "hard_skill",
    "ETL":                  "hard_skill",
    "Data Governance":      "hard_skill",
    "Scikit-learn":         "hard_skill",
    "Hugging Face":         "hard_skill",

    # AI / LLM
    "LLM":                  "hard_skill",
    "OpenAI API":           "hard_skill",
    "gRPC":                 "hard_skill",

    # Security
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

    # Dev Practices
    "Git":                  "hard_skill",
    "Agile":                "hard_skill",
    "Scrum":                "hard_skill",
    "Unit Testing":         "hard_skill",
    "Automation Testing":   "hard_skill",
    "QA":                   "hard_skill",
    "Code Review":          "hard_skill",
    "System Design":        "hard_skill",
    "System Architecture":  "hard_skill",

    # Business / Analysis
    "Business Analysis":    "hard_skill",
    "System Analysis":      "hard_skill",
    "Requirements Gathering": "hard_skill",
    "ERP":                  "hard_skill",
    "CRM":                  "hard_skill",
    "Product Management":   "hard_skill",
    "Project Management":   "soft_skill",
    "Risk Management":      "hard_skill",
    "Change Management":    "hard_skill",
    "Digital Transformation": "hard_skill",

    # Design & UX
    "UX Design":            "hard_skill",
    "UI Design":            "hard_skill",
    "Figma":                "hard_skill",
    "Prototyping":          "hard_skill",

    # Soft Skills
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

# ─────────────────────────────────────────────────────────────────────────────
# ALIASES  (raw lowercase → canonical name)
# ─────────────────────────────────────────────────────────────────────────────
SKILL_ALIASES: dict[str, str] = {

    # AWS variants
    "amazon web services":      "AWS",
    "amazon aws":               "AWS",
    "aws cloud":                "AWS",
    "aws services":             "AWS",
    "aws cloud services":       "AWS",

    # Azure variants
    "microsoft azure":          "Azure",
    "ms azure":                 "Azure",
    "azure cloud":              "Azure",

    # GCP variants
    "google cloud":             "GCP",
    "google cloud platform":    "GCP",
    "gcp cloud":                "GCP",

    # Container / Infra
    "k8s":                      "Kubernetes",
    "docker container":         "Docker",
    "docker containers":        "Docker",
    "cicd":                     "CI/CD",
    "ci cd":                    "CI/CD",
    "ci/cd pipeline":           "CI/CD",
    "github actions":           "GitHub Actions",
    "gitlab ci":                "GitLab CI",
    "gitlab pipeline":          "GitLab CI",
    "aws lambda":               "AWS Lambda",
    "microservice":             "Microservices",
    "micro services":           "Microservices",

    # Languages
    "c sharp":                  "C#",
    "dotnet":                   "C#",
    ".net":                     "C#",
    "dot net":                  "C#",
    "golang":                   "Go",
    "go lang":                  "Go",
    "nodejs":                   "Node.js",
    "node js":                  "Node.js",
    "node.js":                  "Node.js",
    "r programming":            "R",
    "visual c+":                "C++",
    "c plus plus":              "C++",
    "shell script":             "Shell Scripting",
    "bash":                     "Shell Scripting",
    "bash scripting":           "Shell Scripting",
    "pyspark":                  "Spark",
    "apache spark":             "Spark",

    # Web frameworks
    "reactjs":                  "React",
    "react.js":                 "React",
    "react js":                 "React",
    "vuejs":                    "Vue",
    "vue.js":                   "Vue",
    "vue js":                   "Vue",
    "angularjs":                "Angular",
    "angular js":               "Angular",
    "nextjs":                   "Next.js",
    "next js":                  "Next.js",
    "nestjs":                   "NestJS",
    "nest.js":                  "NestJS",
    "spring":                   "Spring Boot",
    "springboot":               "Spring Boot",
    "spring framework":         "Spring Boot",
    "express.js":               "Express",
    "expressjs":                "Express",
    "wpf framework":            "C#",
    "graphql api":              "GraphQL",
    "rest":                     "REST API",
    "restful api":              "REST API",
    "restful":                  "REST API",
    "api":                      "REST API",
    "grpc":                     "gRPC",
    "react native":             "React Native",

    # Frontend
    "html5":                    "HTML",
    "css3":                     "CSS",
    "sass":                     "SASS",
    "scss":                     "SASS",
    "less":                     "CSS",
    "tailwind":                 "Tailwind CSS",

    # Database
    "postgresql":               "PostgreSQL",
    "postgres":                 "PostgreSQL",
    "microsoft sql server":     "SQL",
    "mssql":                    "SQL",
    "mysql server":             "MySQL",
    "nosql":                    "MongoDB",
    "rdbms":                    "SQL",
    "databases":                "SQL",
    "sqlite":                   "SQL",

    # Data & Analytics
    "data analysis":            "Data Analytics",
    "data synthesis":           "Data Analytics",
    "insight generation":       "Data Analytics",
    "data-driven":              "Data Analytics",
    "analytical skills":        "Analytical Thinking",
    "powerbi":                  "Power BI",
    "power query":              "Excel",
    "pivot table":              "Excel",
    "vlookup":                  "Excel",
    "microsoft excel":          "Excel",
    "sas":                      "Data Analytics",
    "sas viya":                 "Data Analytics",
    "spss":                     "Data Analytics",
    "regression analysis":      "Data Modeling",
    "forecasting":              "Data Analytics",
    "data visualization":       "Data Visualization",
    "data modelling":           "Data Modeling",
    "etl pipeline":             "ETL",
    "data pipeline":            "ETL",
    "scikit learn":             "Scikit-learn",
    "sklearn":                  "Scikit-learn",
    "huggingface":              "Hugging Face",
    "hugging face":             "Hugging Face",
    "apache airflow":           "Airflow",
    "apache kafka":             "Kafka",
    "apache hadoop":            "Hadoop",

    # AI / ML
    "artificial intelligence":  "LLM",
    "ai":                       "LLM",
    "ai technologies":          "LLM",
    "llms":                     "LLM",
    "large language model":     "LLM",
    "peft":                     "LLM",
    "openai":                   "OpenAI API",
    "openai apis":              "OpenAI API",
    "chatgpt api":              "OpenAI API",

    # Security
    "information security":     "Cybersecurity",
    "it security":              "Cybersecurity",
    "cyber security":           "Cybersecurity",
    "it infrastructure security": "Network Security",
    "ot network security":      "Network Security",
    "penetration testing (pentest)": "Penetration Testing",
    "pentest":                  "Penetration Testing",
    "pen testing":              "Penetration Testing",
    "vulnerability assessment (va)": "Vulnerability Assessment",
    "vulnerability scanning":   "Vulnerability Assessment",
    "sast":                     "Application Security",
    "dast":                     "Application Security",
    "static application security testing": "Application Security",
    "dynamic application security testing": "Application Security",
    "owasp":                    "OWASP",
    "xss":                      "OWASP",
    "csrf":                     "OWASP",
    "injection attack":         "OWASP",
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
    "design patterns":          "System Design",
    "solution design":          "System Design",
    "system architecture":      "System Architecture",
    "technical specification":  "System Design",
    "code review":              "Code Review",

    # Business
    "business analyst":         "Business Analysis",
    "business process analysis": "Business Analysis",
    "business process design":  "Business Analysis",
    "process reengineering":    "Business Analysis",
    "requirements elicitation": "Requirements Gathering",
    "requirement analysis":     "Requirements Gathering",
    "user story writing":       "Requirements Gathering",
    "functional specification writing": "Requirements Gathering",
    "uat":                      "QA",
    "uat facilitation":         "QA",
    "system analyst":           "System Analysis",
    "system testing":           "QA",
    "erp systems":              "ERP",
    "erp software":             "ERP",
    "erp software development": "ERP",
    "microsoft dynamics":       "ERP",
    "dynamics erp":             "ERP",
    "dynamics 365":             "ERP",
    "crm systems":              "CRM",
    "digital transformation":   "Digital Transformation",
    "digital value creation":   "Digital Transformation",
    "digital solution development": "Digital Transformation",
    "product development":      "Product Management",
    "release management":       "Project Management",
    "project implementation":   "Project Management",
    "process improvement":      "Change Management",
    "risk analysis":            "Risk Management",

    # UX/Design
    "ux":                       "UX Design",
    "ui":                       "UI Design",
    "ui/ux":                    "UX Design",
    "user research":            "UX Design",
    "website design":           "UI Design",
    "web design":               "UI Design",

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
    "stress management":        "Adaptability",
    "resilience":               "Adaptability",
    "quick learning":           "Adaptability",
    "continuous learning":      "Adaptability",
    "continuous improvement":   "Adaptability",
    "coordination":             "Collaboration",
    "planning":                 "Project Management",
    "scheduling":               "Project Management",
    "detail-oriented":          "Attention to Detail",
    "accuracy":                 "Attention to Detail",
    "customer-centric mindset": "Emotional Intelligence",
    "empathy":                  "Emotional Intelligence",
    "emotional intelligence":   "Emotional Intelligence",
}

# ─────────────────────────────────────────────────────────────────────────────
# BLOCKLIST  (ไม่เก็บเลย)
# ─────────────────────────────────────────────────────────────────────────────
SKILL_BLOCKLIST: set[str] = {
    # ภาษา
    "english", "thai", "thai (native)", "english (good command)",
    "english language proficiency", "thai language proficiency",
    "chinese language proficiency", "english proficiency", "jlpt n2",

    # Social media platforms (ไม่ใช่ skill IT)
    "youtube platform knowledge", "youtube marketing", "tiktok marketing",
    "meta marketing", "instagram platform knowledge",
    "facebook platform knowledge", "google platform knowledge",

    # Build tools (ไม่ใช่ skill หลัก)
    "yarn", "webpack", "babel", "vite", "npm", "swc", "webpack.js",

    # Generic/vague
    "programming", "computer literacy", "professionalism",
    "confidentiality", "discretion", "responsibility", "proactiveness",
    "technology", "software", "tools", "platforms",

    # Industry knowledge (vague)
    "energy industry knowledge", "retail industry knowledge",
    "lifestyle ecosystem knowledge", "platform economy",
    "financial domain knowledge", "insurance domain knowledge",
    "insurance", "erp system",

    # Insurance-specific
    "policy (insurance)", "underwriting (insurance)",
    "claims (insurance)", "billing (insurance)",

    # IT Support granular
    "hardware support", "software support", "application installation",
    "it asset management", "system installation", "system configuration",
    "operating system support", "windows operating system", "macos operating system",

    # Data Center ops
    "data center operations", "dc capacity management",
    "server management", "router management",
    "switch management", "equipment operation", "storage management",

    # Certifications (ควรเป็น separate field)
    "cisa", "pmp", "nist", "gdpr", "iso",

    # Tools ไม่ใช่ skill
    "jira", "confluence", "git flow",

    # Noise
    "monitoring", "alerting", "logging", "troubleshooting", "error handling",
    "bug fixing", "debugging", "documentation", "report writing",
    "training", "customer support", "technical support",
    "web banking solutions", "mobile banking solutions",
    "market research", "competitor analysis", "cost/benefit analysis",
    "software selection", "data lineage", "data dictionary",
    "access controls", "data recording systems",
    "security reporting", "security policy development",
    "security policy implementation", "security awareness training",
    "security incident monitoring", "security incident analysis",
    "security solution assessment", "security technology evaluation",
    "pc security", "server security", "incident identification",
    "incident containment", "incident eradication",
    "incident response lifecycle management",
    "translating data insights into action", "data literacy",
    "scada", "historians", "design of experiments (doe)",
    "compliance management", "compliance", "it security regulations",
}

# ─────────────────────────────────────────────────────────────────────────────
# Lookup tables (precomputed for performance)
# ─────────────────────────────────────────────────────────────────────────────
_BLOCKLIST_LOWER: set[str] = {s.lower() for s in SKILL_BLOCKLIST}
_CANONICAL_LOWER: dict[str, str] = {k.lower(): k for k in CANONICAL_SKILLS}
_ALIASES_LOWER:   dict[str, str] = {k.lower(): v for k, v in SKILL_ALIASES.items()}


def normalize(raw: str) -> str | None:
    """
    raw skill name → canonical name  OR  None (blocked / unknown)

    ใช้แทน get_or_create_skill ของเดิม:
        canonical = normalize(raw_name)
        if canonical is None: continue
    """
    if not raw or not raw.strip():
        return None

    cleaned = raw.strip().lower()

    # 1. Blocklist
    if cleaned in _BLOCKLIST_LOWER:
        return None

    # 2. Alias exact match
    if cleaned in _ALIASES_LOWER:
        return _ALIASES_LOWER[cleaned]

    # 3. Canonical exact match (case-insensitive)
    if cleaned in _CANONICAL_LOWER:
        return _CANONICAL_LOWER[cleaned]

    # 4. Partial alias match (ถ้า raw ยาวกว่า alias เช่น "aws cloud computing")
    for alias, canonical in _ALIASES_LOWER.items():
        if len(alias) >= 4 and alias in cleaned:
            return canonical

    # 5. Partial canonical match
    for canon_lower, canon in _CANONICAL_LOWER.items():
        if len(canon_lower) >= 4 and canon_lower in cleaned:
            return canon

    return None  # unknown → ไม่เก็บ