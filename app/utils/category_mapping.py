def map_category(title: str):
    title = title.lower()

    # Software & Web Development
    if any(
        keyword in title
        for keyword in [
            "software engineer",
            "software developer",
            "developer",
            "python",
            "java",
            "javascript",
            "web developer",
            "frontend",
            "backend",
            "fullstack",
            "full-stack",
        ]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6290,
            "sub_category_name": "Engineering - Software",
            "job_role_id": 608,
        }

    # Web Development & Production
    if any(
        keyword in title
        for keyword in ["web developer", "web designer", "wordpress", "html", "css"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6305,
            "sub_category_name": "Web Development & Production",
            "job_role_id": 609,
        }

    # Database Development & Administration
    if any(
        keyword in title
        for keyword in ["database", "dba", "sql", "mysql", "postgresql", "mongodb"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6292,
            "sub_category_name": "Database Development & Administration",
            "job_role_id": 610,
        }

    # Network & Systems Administration
    if any(
        keyword in title
        for keyword in [
            "network",
            "systems admin",
            "system administrator",
            "sysadmin",
            "infrastructure",
        ]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6291,
            "sub_category_name": "Networks & Systems Administration",
            "job_role_id": 611,
        }

    # IT Support & Help Desk
    if any(
        keyword in title
        for keyword in [
            "it support",
            "help desk",
            "helpdesk",
            "support",
            "technical support",
            "it technician",
        ]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6293,
            "sub_category_name": "Help Desk & IT Support",
            "job_role_id": 612,
        }

    # Testing & QA
    if any(
        keyword in title
        for keyword in ["qa", "quality assurance", "test", "tester", "automation"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6294,
            "sub_category_name": "Testing & Quality Assurance",
            "job_role_id": 613,
        }

    # Data Science & Analytics
    if any(
        keyword in title
        for keyword in [
            "data scientist",
            "data analyst",
            "analytics",
            "business intelligence",
            "bi",
            "data engineer",
        ]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6296,
            "sub_category_name": "Business/Systems Analysts",
            "job_role_id": 614,
        }

    # System & Business Analysts
    if any(
        keyword in title
        for keyword in ["analyst", "systems analyst", "business analyst"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6296,
            "sub_category_name": "Business/Systems Analysts",
            "job_role_id": 615,
        }

    # Architect
    if any(
        keyword in title
        for keyword in ["architect", "solution architect", "enterprise architect"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6304,
            "sub_category_name": "Architects",
            "job_role_id": 616,
        }

    # Security
    if any(
        keyword in title
        for keyword in [
            "security",
            "cyber",
            "penetration",
            "information security",
            "security analyst",
        ]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6299,
            "sub_category_name": "Security",
            "job_role_id": 617,
        }

    # IT Management & Leadership
    if any(
        keyword in title
        for keyword in [
            "it manager",
            "it director",
            "team lead",
            "project manager",
            "scrum master",
            "agile",
        ]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6301,
            "sub_category_name": "Management",
            "job_role_id": 618,
        }

    # IT Consultant
    if any(
        keyword in title
        for keyword in ["consultant", "consulting", "professional services"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6298,
            "sub_category_name": "Consultants",
            "job_role_id": 619,
        }

    # IT Operation & Support
    if any(
        keyword in title
        for keyword in ["computer operator", "operations", "it operations"]
    ):
        return {
            "main_category_id": 6281,
            "main_category_name": "Information & Communication Technology",
            "sub_category_id": 6306,
            "sub_category_name": "Computer Operators",
            "job_role_id": 620,
        }

    return None
