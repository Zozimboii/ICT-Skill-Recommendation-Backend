# main.py
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.core.cors import setup_cors

from app.models import user, job, skill, transcript, recommendation
from app.router import api_router

def create_app() -> FastAPI:
    app = FastAPI(title="ICT Job Skill Recommendation API")
    setup_cors(app)
    app.include_router(api_router) 
    return app


app = create_app()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health Check",
)
async def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "ICT Skill Recommendation API",
            "version": "1.0.0",
        },
    )