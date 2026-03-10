# app/utils/skill_groups.py
"""
Phase 2: จัดกลุ่ม skill ตาม keyword matching
ใช้เพราะ Skill model ไม่มี category FK ตรงๆ
"""

SKILL_GROUPS: dict[str, list[str]] = {

    "Cloud & Infrastructure": [
        "aws", "amazon web services", "azure", "gcp", "google cloud",
        "cloud", "cloud computing", "cloud architecture",
        "terraform", "ansible", "infrastructure", "iac",
        "kubernetes", "docker", "container", "containerization",
        "devops", "ci/cd", "jenkins", "gitlab ci", "github actions",
        "linux", "ubuntu", "redhat", "centos",
        "vmware", "openstack", "server", "load balancing",
    ],

    "Programming & Development": [
        "python", "java", "javascript", "typescript",
        "c++", "c#", "go", "golang", "rust",
        "kotlin", "swift", "php", "ruby",
        "scala", "r", "matlab", "dart",
        "flutter", "android", "ios",

        "react", "vue", "angular",
        "node", "nodejs",
        "spring", "spring boot",
        "django", "flask", "fastapi",
        "laravel", "express",

        "backend", "frontend", "fullstack",
        "rest api", "graphql",
    ],

    "Data & AI": [
        "sql", "mysql", "postgresql", "mongodb",
        "redis", "elasticsearch",
        "data analysis", "data analytics",
        "data science",
        "machine learning", "ml",
        "deep learning", "ai",
        "nlp", "computer vision",

        "pandas", "numpy",
        "tensorflow", "pytorch",
        "spark", "hadoop",
        "airflow", "kafka",

        "tableau", "power bi",
        "excel", "statistics",
        "etl", "data warehouse",
        "data pipeline",
    ],

    "Cybersecurity": [
        "security", "cybersecurity",
        "penetration testing", "pentest",
        "owasp",
        "siem", "soc",
        "firewall", "ids", "ips",
        "encryption", "ssl", "tls",
        "iam", "identity access",
        "vulnerability", "threat",
        "network security",
        "information security",
        "iso 27001", "nist",
    ],

    "Software Architecture": [
        "system architecture",
        "software architecture",
        "microservices",
        "distributed systems",
        "scalability",
        "high availability",
        "event-driven",
        "design patterns",
        "system design",
    ],

    "Testing & QA": [
        "unit testing",
        "integration testing",
        "automation testing",
        "qa", "quality assurance",
        "selenium", "cypress",
        "jest", "mocha",
        "test automation",
        "tdd", "bdd",
    ],

    "DevOps & Monitoring": [
        "monitoring", "observability",
        "prometheus", "grafana",
        "logging", "elk",
        "logstash", "kibana",
        "alerting",
        "incident management",
        "site reliability", "sre",
    ],

    "Database & Storage": [
        "database", "dbms",
        "mysql", "postgresql",
        "oracle", "sql server",
        "mongodb", "cassandra",
        "dynamodb",
        "data modeling",
        "data architecture",
    ],

    "UI/UX & Design": [
        "figma", "sketch",
        "ux", "ui",
        "user experience",
        "user interface",
        "wireframe",
        "prototype",
        "design thinking",
        "interaction design",
        "usability",
        "css", "html",
    ],

    "Business & Product": [
        "product management",
        "business analysis",
        "business analyst",
        "requirements gathering",
        "stakeholder management",
        "roadmap",
        "market research",
        "kpi",
        "okr",
        "data-driven decision",
    ],

    "Management & Leadership": [
        "leadership",
        "team leadership",
        "project management",
        "agile", "scrum", "kanban",
        "pmp",
        "team management",
        "mentoring",
        "coaching",
        "strategy",
        "budget management",
        "decision making",
    ],

    "Communication & Soft Skills": [
        "communication",
        "presentation",
        "negotiation",
        "teamwork",
        "collaboration",
        "problem solving",
        "critical thinking",
        "analytical thinking",
        "adaptability",
        "time management",
        "conflict resolution",
    ],

    "IT Operations & Support": [
        "technical support",
        "it support",
        "system administration",
        "server administration",
        "network troubleshooting",
        "hardware support",
        "installation",
        "system monitoring",
        "helpdesk",
    ],

    "Other": [],  # catch-all
}


def get_skill_group(skill_name: str) -> str:
    """Return group name for a skill based on keyword matching."""
    name_lower = skill_name.lower()
    for group, keywords in SKILL_GROUPS.items():
        if group == "Other":
            continue
        for kw in keywords:
            if kw in name_lower or name_lower in kw:
                return group
    return "Other"


def group_skills(skills: list[dict]) -> dict[str, list[dict]]:
    """
    skills: list of {"skill_name": str, ...}
    returns: {"Cloud & Infrastructure": [...], "Programming": [...], ...}
    Only includes groups that have at least 1 skill.
    """
    grouped: dict[str, list[dict]] = {}
    for skill in skills:
        group = get_skill_group(skill["skill_name"])
        grouped.setdefault(group, []).append(skill)

    # เรียง group ตามลำดับใน SKILL_GROUPS
    ordered = {}
    for group in SKILL_GROUPS:
        if group in grouped:
            ordered[group] = grouped[group]
    return ordered