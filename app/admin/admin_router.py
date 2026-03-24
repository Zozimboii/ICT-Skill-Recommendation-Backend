# app/admin/admin.router.py

import traceback
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.admin.admin_schema import (
    AdminStats,
    AdminUserItem,
    AdminUserUpdate,
    AdminJobItem,
    AdminSkillItem,
    AdminSkillCreate,
    ScrapeRequest,
    ScrapeResponse,
)
from app.scraping.job_scraper_service import JobScraperService
from app.admin.admin_service import AdminService

admin_service = AdminService()

router = APIRouter()
# ── Guard: admin only ──────────────────────────────────────────────
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── Stats ──────────────────────────────────────────────────────────
@router.get("/stats", response_model=AdminStats)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return admin_service.get_stats(db)


# ── Users ──────────────────────────────────────────────────────────
@router.get("/users", response_model=list[AdminUserItem])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return admin_service.list_users(db, skip, limit)


@router.patch("/users/{user_id}", response_model=AdminUserItem)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = admin_service.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}/delete")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ok = admin_service.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "deleted"}

# ── Jobs ───────────────────────────────────────────────────────────
@router.get("/jobs", response_model=dict)
def list_jobs(
    keyword: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    jobs, total = admin_service.list_jobs(db, keyword, skip, limit)
    return {"total": total, "data": [j.model_dump() for j in jobs]}


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ok = admin_service.delete_job(db, job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "deleted"}


# ── Skills ─────────────────────────────────────────────────────────
@router.get("/skills", response_model=list[AdminSkillItem])
def list_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return admin_service.list_skills(db, skip, limit)


@router.post("/skills", response_model=AdminSkillItem, status_code=201)
def create_skill(
    data: AdminSkillCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return admin_service.create_skill(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/skills/{skill_id}")
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ok = admin_service.delete_skill(db, skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"message": "deleted"}


# ── Scrape trigger ─────────────────────────────────────────────────
@router.post("/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    data: ScrapeRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
   

    try:
        service = JobScraperService()
        added = await asyncio.wait_for(
            asyncio.to_thread(service.run_scraping, data.limit),
            timeout=300.0,
        )
        return ScrapeResponse(message="Scrape completed", jobs_added=added or 0)
    except asyncio.TimeoutError:
        return ScrapeResponse(message="Scrape started (running in background)", jobs_added=0)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))