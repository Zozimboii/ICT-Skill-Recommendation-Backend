# backend/app/main.py

from fastapi import FastAPI, Depends, Query , HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, select

from app.database import get_db
from app.models import JobsSkill, JobCountBySubCategory, JobSkillCountBySkillname, JobSkillsWithCategories ,User
from app.schemas import LoginRequest , RegisterRequest
from app.security import hash_password, verify_password

    
app = FastAPI(title="ICT Job Skill Recommendation API")

# ✅ CORS (ให้ frontend เรียกได้)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    rows = (
        db.query(JobsSkill.job_id, JobsSkill.title)
        .group_by(JobsSkill.job_id, JobsSkill.title)
        .limit(50)
        .all()
    )
    return [{"job_id": r[0], "title": r[1]} for r in rows]

@app.get("/searchjobs")
def search_jobs(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db),
):
    keyword = q.strip().lower()

    # 1) หา sub_category ที่ match จากชื่อ sub_category_name
    matches = (
        db.query(
            JobCountBySubCategory.sub_category_id,
            JobCountBySubCategory.sub_category_name,
            JobCountBySubCategory.job_count,
        )
        .filter(func.lower(JobCountBySubCategory.sub_category_name).like(f"%{keyword}%"))
        .order_by(JobCountBySubCategory.job_count.desc())
        .limit(limit)
        .all()
    )

    if not matches:
        return {
            "sub_category_id": "",
            "sub_category_name": keyword,
            "job_count": 0,
            "top_categories": [],
            "related_sub_categories": [],
        }

    # เลือก sub_category แรกเป็นหลัก
    main_sub_id, main_sub_name, main_job_count = matches[0]

    # 2) Top categories (main_category และ sub_category) สำหรับ sub_category นี้
    top_categories = (
        db.query(
            JobCountBySubCategory.main_category_id,
            JobCountBySubCategory.main_category_name,
            JobCountBySubCategory.sub_category_id,
            JobCountBySubCategory.sub_category_name,
            JobCountBySubCategory.job_count,
        )
        .filter(JobCountBySubCategory.sub_category_id == main_sub_id)
        .order_by(JobCountBySubCategory.job_count.desc())
        .all()
    )

    # 3) Related sub_categories: sub_category อื่นที่มี main_category เดียวกัน
    main_category_id = top_categories[0][0] if top_categories else None

    related = (
        db.query(
            JobCountBySubCategory.sub_category_id,
            JobCountBySubCategory.sub_category_name,
            JobCountBySubCategory.job_count,
        )
        .filter(JobCountBySubCategory.main_category_id == main_category_id)
        .filter(JobCountBySubCategory.sub_category_id != main_sub_id)
        .order_by(JobCountBySubCategory.job_count.desc())
        .limit(10)
        .all()
    )

    return {
        "sub_category_id": int(main_sub_id),
        "sub_category_name": main_sub_name,
        "job_count": int(main_job_count),
        "top_categories": [
            {
                "main_category_id": r[0],
                "main_category_name": r[1],
                "sub_category_id": r[2],
                "sub_category_name": r[3],
                "job_count": int(r[4]),
            }
            for r in top_categories
        ],
        "related_sub_categories": [
            {"sub_category_id": int(r[0]), "sub_category_name": r[1], "job_count": int(r[2])} 
            for r in related
        ],
    }

@app.get("/skills/search")
def skill_search(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db),
):
    keyword = q.strip().lower()

    # 1) หา skill ที่ match จากตารางสรุป (นับจำนวน job ที่เจอสกิล)
    matches = (
        db.query(
            JobSkillCountBySkillname.skill_name,
            JobSkillCountBySkillname.skill_type,
            JobSkillCountBySkillname.job_skill_count.label("job_count"),
        )
        .filter(func.lower(JobSkillCountBySkillname.skill_name).like(f"%{keyword}%"))
        .order_by(JobSkillCountBySkillname.job_skill_count.desc())
        .limit(limit)
        .all()
    )

    if not matches:
        return {
            "skill_name": keyword,
            "skill_type": "",
            "job_count": 0,
            "top_subcategories": [],
            "related_skills": [],
        }

    # เลือกตัวหลักเป็นอันดับ 1
    main_skill_name, main_skill_type, main_job_count = matches[0]

    # 2) หา job_id ที่มีสกิลนี้ (exact match แบบ case-insensitive)
    job_ids_subq = (
        db.query(JobsSkill.job_id)
        .filter(func.lower(JobsSkill.skill_name) == func.lower(main_skill_name))
        .subquery()
    )
    job_ids_select = select(job_ids_subq.c.job_id)

    # 3) Top sub-categories ที่พบสกิลนี้
    top_subcategories = (
        db.query(
            JobSkillsWithCategories.main_category_id,
            JobSkillsWithCategories.main_category_name,
            JobSkillsWithCategories.sub_category_id,
            JobSkillsWithCategories.sub_category_name,
            func.count(distinct(JobSkillsWithCategories.job_id)).label("count"),
        )
        .filter(JobSkillsWithCategories.job_id.in_(job_ids_select))
        .group_by(
            JobSkillsWithCategories.main_category_id,
            JobSkillsWithCategories.main_category_name,
            JobSkillsWithCategories.sub_category_id,
            JobSkillsWithCategories.sub_category_name,
        )
        .order_by(func.count(distinct(JobSkillsWithCategories.job_id)).desc())
        .limit(10)
        .all()
    )

    # 4) related skills: สกิลอื่นที่อยู่ใน job เดียวกัน
    related = (
        db.query(
            JobsSkill.skill_name,
            func.count(distinct(JobsSkill.job_id)).label("count"),
        )
        .filter(JobsSkill.job_id.in_(job_ids_select))
        .filter(func.lower(JobsSkill.skill_name) != func.lower(main_skill_name))
        .group_by(JobsSkill.skill_name)
        .order_by(func.count(distinct(JobsSkill.job_id)).desc())
        .limit(20)
        .all()
    )

    return {
        "skill_name": main_skill_name,
        "skill_type": main_skill_type,
        "job_count": int(main_job_count),
        "top_subcategories": [
            {
                "main_category_id": r[0],
                "main_category_name": r[1],
                "sub_category_id": r[2],
                "sub_category_name": r[3],
                "count": int(r[4]),
            }
            for r in top_subcategories
        ],
        "related_skills": [{"skill_name": r[0], "count": int(r[1])} for r in related],
    }

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # 1. ตรวจสอบว่ามี user นี้หรือไม่
    user = db.query(User).filter(User.username == data.username).first()

    # 2. ตรวจสอบ password
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # 3. login สำเร็จ
    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username
        }
    }


@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=data.username,
        password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "user_id": user.id
    }

