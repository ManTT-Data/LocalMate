"""
LocalMate Da Nang - Danang Tourism Super Agent API.

FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.shared.db.session import engine
from app.shared.integrations.neo4j_client import neo4j_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    yield
    # Shutdown
    await neo4j_client.close()
    await engine.dispose()


app = FastAPI(
    title="LocalMate Da Nang",
    description="Danang Tourism Super Agent API - AI Travel Planner",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns status of the application and connected services.
    """
    neo4j_ok = await neo4j_client.verify_connectivity()
    return {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "neo4j": "connected" if neo4j_ok else "disconnected",
        },
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "LocalMate Da Nang API",
        "version": "0.1.0",
        "docs": "/docs",
    }
