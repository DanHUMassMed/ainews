from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.public import router as public_router
from backend.app.api.editorial import router as editorial_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Industry News Daily - Self-hosted briefing publication & Hermes Editorial API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for intranet frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router, prefix=settings.API_V1_STR)
app.include_router(editorial_router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
    }
