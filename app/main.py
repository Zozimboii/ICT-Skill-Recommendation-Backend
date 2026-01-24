from fastapi import FastAPI
from app.core.cors import setup_cors
from app.api.v1.router import router as api_v1_router

def create_app() -> FastAPI:
    app = FastAPI(title="ICT Job Skill Recommendation API")
    setup_cors(app)
    app.include_router(api_v1_router)
    return app

app = create_app()
