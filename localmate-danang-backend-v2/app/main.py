"""
LocalMate Da Nang V2 - Multi-Modal Contextual Agent API.

FastAPI application entry point with /chat endpoint for testing.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.planner.router import router as planner_router
from app.users.router import router as users_router
from app.itineraries.router import router as itineraries_router
from app.auth.router import router as auth_router
from app.shared.db.session import engine
from app.shared.integrations.neo4j_client import neo4j_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup - preload SigLIP model
    try:
        from app.shared.integrations.siglip_client import get_siglip_client
        siglip = get_siglip_client()
        print(f"✅ SigLIP ready: {siglip.is_loaded}")
    except Exception as e:
        print(f"⚠️ SigLIP not loaded (image search disabled): {e}")
    
    yield
    
    # Shutdown
    await neo4j_client.close()
    await engine.dispose()


app = FastAPI(
    title="LocalMate Da Nang V2",
    description="""
## Multi-Modal Contextual Agent (MMCA) API

Intelligent travel assistant for Da Nang with 3 MCP tools + Trip Planner:

### Tools Available:
1. **retrieve_context_text** - Semantic search in text descriptions (reviews, menus)
2. **retrieve_similar_visuals** - Image similarity search (find similar vibes)
3. **find_nearby_places** - Spatial search (find places near a location)

### Trip Planner:
- Create plans and add places
- Optimize route with TSP algorithm
- Reorder, replace, and manage places

### Examples:
- "Tìm quán cafe gần bãi biển Mỹ Khê"
- "Nhà hàng hải sản nào được review tốt?"
- "Quán nào có không gian xanh mát?" (with image_url)
""",
    version="0.3.0",
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

# Include API routers
app.include_router(api_router, prefix="/api/v1", tags=["Chat"])
app.include_router(planner_router, prefix="/api/v1", tags=["Trip Planner"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(itineraries_router, prefix="/api/v1", tags=["Itineraries"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])

# Upload router
from app.upload import router as upload_router
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])


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
