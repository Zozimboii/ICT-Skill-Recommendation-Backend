# scripts/seed.py
# รันครั้งแรกเพื่อสร้างข้อมูลเริ่มต้น
# Usage: py -m scripts.seed

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.skill import Skill, SkillCategory
from app.utils.category_config import SUB_CATEGORIES
from app.utils.skill_dict import SKILL_DICT


def seed_admin(db):
    if db.query(User).filter(User.email == "admin@gmail.com").first():
        print("[SKIP] Admin already exists")
        return

    db.add(User(
        email="admin@gmail.com",
        first_name="Admin",
        last_name="System",
        password_hash='$argon2id$v=19$m=65536,t=3,p=4$kRLCGCMkREgppVQqBQBgLA$mTTMUexJrCglP8WPIMqXKWM32VOZg1qMm7lVMQyCJew',
        role="admin"
    ))
    db.flush()
    print("✅ Admin created — email: admin@gmail.com / password: admin1234")


def seed_categories(db):
    inserted = 0
    for cat in SUB_CATEGORIES:
        exists = db.query(SkillCategory).filter(
            SkillCategory.id == cat["id"]
        ).first()
        if exists:
            continue
        db.add(SkillCategory(id=cat["id"], name=cat["name"]))
        inserted += 1

    db.flush()
    print(f"✅ Categories: {inserted} inserted ({len(SUB_CATEGORIES) - inserted} already existed)")


def seed_skills(db):
    """Seed skills จาก SKILL_DICT เพื่อให้ transcript matching หา skill เจอ"""
    inserted = 0
    skipped  = 0

    for skill_name, skill_type in SKILL_DICT.items():
        exists = db.query(Skill).filter(Skill.name == skill_name).first()
        if exists:
            skipped += 1
            continue
        db.add(Skill(name=skill_name, skill_type=skill_type))
        inserted += 1

    db.flush()
    print(f"✅ Skills: {inserted} inserted ({skipped} already existed)")


DEFAULT_ALIASES = [
    # AI / ML
    ("artificial intelligence",     "ai"),
    ("machine learning",            "machine learning"),
    ("ml",                          "machine learning"),
    ("deep learning",               "ai"),
    ("neural network",              "ai"),
    ("nlp",                         "llm"),
    ("natural language processing", "llm"),
    ("large language model",        "llm"),
    ("generative ai",               "llm"),
    ("gen ai",                      "llm"),
    # Database
    ("postgresql",                  "postgres"),
    ("mysql",                       "sql"),
    ("rdbms",                       "database systems"),
    ("nosql",                       "nosql databases"),
    # Cloud
    ("amazon web services",         "aws"),
    ("microsoft azure",             "azure"),
    ("google cloud",                "cloud"),
    ("gcp",                         "cloud"),
    # Web
    ("js",                          "javascript"),
    ("typescript",                  "javascript"),
    ("reactjs",                     "react"),
    ("react.js",                    "react"),
    ("vue.js",                      "vue"),
    ("nodejs",                      "node.js"),
    # Frameworks
    ("scikit-learn",                "Scikit-learn"),
    ("sklearn",                     "Scikit-learn"),
    ("pytorch",                     "PyTorch"),
    ("tensorflow",                  "TensorFlow"),
    # DevOps
    ("k8s",                         "Kubernetes"),
    ("ci/cd",                       "git"),
    ("cicd",                        "git"),
    # Business
    ("ba",                          "business analysis"),
    ("sap",                         "erp"),
    ("salesforce",                  "crm"),
    ("power bi",                    "power bi"),
    ("powerbi",                     "power bi"),
    ("excel",                       "microsoft excel"),
    # Soft Skills
    ("problem-solving",             "problem solving"),
    ("communication skills",        "communication"),
    ("teamwork",                    "collaboration"),
    ("team player",                 "collaboration"),
    ("critical thinking",           "analytical thinking"),
    ("data driven",                 "data-driven mindset"),
    ("data-driven",                 "data-driven mindset"),
]


def seed_aliases(db):
    from app.models.skill import Skill, SkillAlias
    inserted = skipped = not_found = 0

    for alias_str, skill_name in DEFAULT_ALIASES:
        # ค้นหา skill ที่ canonical ชี้ไป
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill:
            print(f"  [SKIP alias] skill '{skill_name}' ไม่อยู่ใน DB")
            not_found += 1
            continue

        exists = db.query(SkillAlias).filter(SkillAlias.alias == alias_str).first()
        if exists:
            skipped += 1
            continue

        db.add(SkillAlias(alias=alias_str, skill_id=skill.id))
        inserted += 1

    db.flush()
    print(f"✅ Aliases: {inserted} inserted ({skipped} existed, {not_found} skill not found)")

def main():
    db = SessionLocal()
    try:
        print("🌱 Seeding database...")
        seed_categories(db)
        seed_skills(db)
        seed_aliases(db)
        seed_admin(db)
        db.commit()
        print("\n✅ Seed complete!")
        print("   Admin login: admin@gmail.com / admin1234")
        print("   ⚠️  กรุณาเปลี่ยน password หลัง login ครั้งแรก")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()