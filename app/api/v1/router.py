# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1 import skills, jobs, advisor, trends, auth , chat

router = APIRouter(prefix="/api/v1")

router.include_router(skills.router, prefix="/skills", tags=["skills"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
router.include_router(advisor.router, prefix="/advisor", tags=["advisor"])
router.include_router(trends.router, prefix="/trends", tags=["trends"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])