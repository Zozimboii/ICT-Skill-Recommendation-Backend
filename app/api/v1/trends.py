# backend/app/api/v1/trends.py
from fastapi import APIRouter, Query
from app.services.trends_service import jobsdb_trend

router = APIRouter()

@router.get("/jobsdb")
def trends_jobsdb(limit: int = Query(20, ge=1, le=100)):
    # GET /api/v1/trends/jobsdb?limit=20
    return jobsdb_trend(limit=limit)
