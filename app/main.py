from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.v1.router import router as api_v1_router
from app.core.cors import setup_cors


def create_app() -> FastAPI:
    app = FastAPI(title="ICT Job Skill Recommendation API")
    setup_cors(app)
    app.include_router(api_v1_router)
    return app


app = create_app()



@app.get("/health", 
         status_code=status.HTTP_200_OK,
         tags=["Health"],
         summary="Health Check",
         description="Check if the API is running and responsive")
async def health_check():
    """
    Health check endpoint for Docker HEALTHCHECK and monitoring
    
    Returns:
        - status: API status (healthy/unhealthy)
        - timestamp: Current server time
        - uptime: Server uptime in seconds
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "ICT Skill Recommendation API",
            "version": "1.0.0"
        }
    )
