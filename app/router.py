# app/router.py
from fastapi import APIRouter

from app.auth.auth_router       import router as auth_router
from app.admin.admin_router     import router as admin_router
from app.assessment.assessment_router import router as assessment_router
from app.dashboard.dashboard_router   import router as dashboard_router
from app.jobs.jobs_router       import router as jobs_router
from app.transcript.transcript_router import router as transcript_router
from app.trends.trends_router   import router as trends_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router,       prefix="/auth",       tags=["Auth"])
api_router.include_router(admin_router,      prefix="/admin",      tags=["Admin"])
api_router.include_router(assessment_router, prefix="/assessment", tags=["Assessment"])
api_router.include_router(dashboard_router,  prefix="/dashboard",  tags=["Dashboard"])
api_router.include_router(jobs_router,       prefix="/jobs",       tags=["Jobs"])
api_router.include_router(transcript_router, prefix="/transcript", tags=["Transcript"])
api_router.include_router(trends_router,     prefix="/trends",     tags=["Trends"])