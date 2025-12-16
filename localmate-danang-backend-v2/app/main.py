"""
LocalMate Da Nang V2 - Multi-Modal Contextual Agent API.

FastAPI application entry point with /chat endpoint for testing.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
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
    title="LocalMate Da Nang V2",
    description="""
## Multi-Modal Contextual Agent (MMCA) API

Intelligent travel assistant for Da Nang with 3 MCP tools:

### Tools Available:
1. **retrieve_context_text** - Semantic search in text descriptions (reviews, menus)
2. **retrieve_similar_visuals** - Image similarity search (find similar vibes)
3. **find_nearby_places** - Spatial search (find places near a location)

### How to Use:
Use the `/chat` endpoint to interact with the agent in natural language.

### Examples:
- "Tìm quán cafe gần bãi biển Mỹ Khê"
- "Nhà hàng hải sản nào được review tốt?"
- "Quán nào có không gian xanh mát?" (with image_url)
""",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware - allow all for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1", tags=["Chat"])


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns status of the application and connected services.
    """
    neo4j_ok = await neo4j_client.verify_connectivity()
    return {
        "status": "healthy",
        "version": "0.2.0",
        "services": {
            "neo4j": "connected" if neo4j_ok else "disconnected",
        },
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "LocalMate Da Nang V2 - MMCA API",
        "version": "0.2.0",
        "docs": "/docs",
        "description": "Multi-Modal Contextual Agent for Da Nang Tourism",
    }
