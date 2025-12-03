"""
FastAPI Application Entry Point

Khởi tạo FastAPI app và mount router của 2 agent:
- Planner App: /api/v1/planner/*
- Guide App: /api/v1/guide/*
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.shared.core.exceptions import setup_exception_handlers
from app.planner_app.api.router import router as planner_router
from app.guide_app.api.router import router as guide_router

# Create FastAPI app
app = FastAPI(
    title="LocalMate Da Nang API",
    description="AI-powered travel assistant for Da Nang with dual agent system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Mount routers for 2 agents
app.include_router(planner_router, prefix="/api/v1/planner", tags=["Planner App"])
app.include_router(guide_router, prefix="/api/v1/guide", tags=["Guide App"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LocalMate Da Nang API",
        "status": "running",
        "agents": ["planner", "guide"],
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "services": {
            "postgres": "connected",  # TODO: Add actual health checks
            "neo4j": "connected",
            "redis": "connected",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
