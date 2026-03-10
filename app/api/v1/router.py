# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1 import  auth, jobs,trends ,transcript ,admin, dashboard


router = APIRouter(prefix="/api/v1")

# router.include_router(skills.router, prefix="/skills", tags=["skills"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# router.include_router(advisor.router, prefix="/advisor", tags=["advisor"])
router.include_router(trends.router, prefix="/trends", tags=["trends"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
# router.include_router(insert.router, prefix="/insert", tags=["insert"])
# router.include_router(chat.router, prefix="/chat", tags=["chat"])
# router.include_router(positions.router, prefix="/positions", tags=["positions"])
router.include_router(transcript.router, prefix="/transcript", tags=["transcript"])

router.include_router(dashboard.router,prefix="/dashboard", tags=["dashboard"] )
router.include_router(admin.router,prefix="/admin", tags=["admin"])