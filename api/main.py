"""
FastAPI RAG Application
Endpoints for place recommendations in Da Nang
Combines vector search (Supabase) with graph data (Neo4j)
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn

from rag_service import RAGSearchService
from neo4j_service import Neo4jService
from image_service import ImageSearchService


# Initialize
app = FastAPI(
    title="Da Nang Tourism RAG API",
    description="""
# 🏖️ Da Nang Tourism API

AI-powered destination recommendations combining:
- **Vector Search** (Supabase): Semantic text matching
- **Graph Database** (Neo4j): Relationships, nearby places, categories

## Features
- Natural language search in Vietnamese/English
- Place details with photos, reviews
- Nearby place recommendations
- Category-based filtering
- Location-based search
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGSearchService()
neo4j_service: Optional[Neo4jService] = None
image_service: Optional[ImageSearchService] = None

# Lazy load services to handle connection errors gracefully
def get_neo4j_service() -> Neo4jService:
    global neo4j_service
    if neo4j_service is None:
        neo4j_service = Neo4jService()
    return neo4j_service

def get_image_service() -> ImageSearchService:
    global image_service
    if image_service is None:
        image_service = ImageSearchService()
    return image_service


# ============================================================================
# Pydantic Models
# ============================================================================

class SearchRequest(BaseModel):
    """Search request body"""
    query: str = Field(..., description="Natural language search query", example="quán cafe view đẹp")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    rating_min: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating filter")


class PlaceResult(BaseModel):
    """Search result item"""
    place_id: str = Field(..., description="Unique place identifier")
    name: str = Field(..., description="Place name")
    category: str = Field(..., description="Place category")
    rating: float = Field(..., description="Rating 0-5")
    score: float = Field(..., description="Search relevance score")
    description: str = Field("", description="Short description")
    llm_summary: str = Field("", description="AI-generated summary")
    source_types: List[str] = Field(default_factory=list, description="Matched embedding types")


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[PlaceResult]
    total: int


class ReviewModel(BaseModel):
    """Review data"""
    text: str
    rating: int
    reviewer: str


class NearbyPlaceModel(BaseModel):
    """Nearby place with distance"""
    place_id: str
    name: str
    category: str
    rating: float
    distance_km: float


class CoordinatesModel(BaseModel):
    """Geographic coordinates"""
    lat: float
    lng: float


class PlaceDetailsResponse(BaseModel):
    """Complete place details"""
    place_id: str
    name: str
    category: str
    rating: float
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    description: Optional[str] = None
    specialty: Optional[str] = None
    price_range: Optional[str] = None
    coordinates: CoordinatesModel
    photos_count: int
    reviews_count: int
    photos: List[str] = Field(default_factory=list, description="Photo URLs/paths")
    reviews: List[ReviewModel] = Field(default_factory=list, description="Sample reviews")
    nearby_places: List[NearbyPlaceModel] = Field(default_factory=list, description="Places nearby")
    same_category: List[Dict[str, Any]] = Field(default_factory=list, description="Similar places")


class LocationSearchRequest(BaseModel):
    """Location-based search request"""
    lat: float = Field(..., description="Latitude", example=16.048)
    lng: float = Field(..., description="Longitude", example=108.247)
    radius_km: float = Field(2.0, ge=0.1, le=10, description="Search radius in km")
    limit: int = Field(10, ge=1, le=50, description="Maximum results")


class ImageSearchResult(BaseModel):
    """Image search result item"""
    place_id: str = Field(..., description="Unique place identifier")
    name: str = Field(..., description="Place name")
    category: str = Field(..., description="Place category")
    rating: float = Field(..., description="Rating 0-5")
    similarity: float = Field(..., description="Image similarity score")
    matched_images: int = Field(..., description="Number of matched images")
    scene_type: str = Field(..., description="Scene type of best match")


class ImageSearchResponse(BaseModel):
    """Image search response"""
    results: List[ImageSearchResult]
    total: int
    scene_filter: Optional[str] = None


# ============================================================================
# Search Endpoints (RAG - Vector Search)
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """API information and available endpoints"""
    return {
        "name": "Da Nang Tourism RAG API",
        "version": "2.0.0",
        "description": "AI-powered place recommendations for Da Nang",
        "endpoints": {
            "search": {
                "POST /search": "Semantic search with query body",
                "GET /search?q=...": "Simple search via URL",
                "GET /search/category/{category}": "Category-based search",
                "POST /search/location": "Search by GPS coordinates",
                "POST /search/image": "Image-based search (upload image)"
            },
            "places": {
                "GET /places/{place_id}": "Get place details from Neo4j",
                "GET /places/{place_id}/nearby": "Get nearby places"
            },
            "system": {
                "GET /health": "Health check",
                "GET /docs": "Swagger UI",
                "GET /redoc": "ReDoc documentation"
            }
        }
    }


@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_places(request: SearchRequest):
    """
    🔍 Semantic search for places
    
    Uses AI embeddings to find places matching your natural language query.
    Supports Vietnamese and English.
    
    **Examples:**
    - "quán cafe view đẹp" 
    - "phở ngon giá rẻ"
    - "romantic dinner spot"
    - "best seafood restaurant"
    """
    try:
        results = rag_service.search_text(
            query=request.query,
            max_results=request.max_results,
            rating_min=request.rating_min
        )
        
        return SearchResponse(
            query=request.query,
            results=[
                PlaceResult(
                    place_id=r.place_id,
                    name=r.name,
                    category=r.category,
                    rating=r.rating,
                    score=round(r.similarity, 4),
                    description=r.description[:300] if r.description else "",
                    llm_summary=r.llm_text,
                    source_types=r.source_types
                ) for r in results
            ],
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_places_get(
    q: str = Query(..., description="Search query", example="cafe view đẹp"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating")
):
    """
    🔍 Simple search via URL query parameters
    
    Convenient for browser testing and simple integrations.
    """
    request = SearchRequest(query=q, max_results=limit, rating_min=rating_min)
    return await search_places(request)


@app.get("/search/category/{category}", response_model=SearchResponse, tags=["Search"])
async def search_by_category(
    category: str,
    context: Optional[str] = Query(None, description="Additional context", example="view đẹp"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    🏷️ Search within a specific category
    
    **Available categories:**
    - `cafe` - Coffee shops
    - `pho` - Pho restaurants  
    - `banh_mi` - Banh mi shops
    - `seafood` - Seafood restaurants
    - `restaurant` - General restaurants
    - `bar` - Bars and pubs
    - `hotel` - Hotels and resorts
    """
    try:
        results = rag_service.search_by_category(
            category=category,
            query_context=context,
            max_results=limit
        )
        
        return SearchResponse(
            query=f"category:{category} {context or ''}",
            results=[
                PlaceResult(
                    place_id=r.place_id,
                    name=r.name,
                    category=r.category,
                    rating=r.rating,
                    score=round(r.similarity, 4),
                    description=r.description[:300] if r.description else "",
                    llm_summary="",
                    source_types=r.source_types
                ) for r in results
            ],
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/location", tags=["Search"])
async def search_by_location(request: LocationSearchRequest):
    """
    📍 Search places near a GPS location
    
    Find places within a radius of your current location.
    Uses Neo4j spatial queries for accurate distance calculations.
    """
    try:
        neo4j = get_neo4j_service()
        places = neo4j.search_by_location(
            lat=request.lat,
            lng=request.lng,
            radius_km=request.radius_km,
            limit=request.limit
        )
        
        return {
            "location": {"lat": request.lat, "lng": request.lng},
            "radius_km": request.radius_km,
            "results": [
                {
                    "place_id": p.place_id,
                    "name": p.name,
                    "category": p.category,
                    "rating": p.rating,
                    "distance_km": p.distance_km
                } for p in places
            ],
            "total": len(places)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {str(e)}")


@app.post("/search/image", response_model=ImageSearchResponse, tags=["Search"])
async def search_by_image(
    image: UploadFile = File(..., description="Image file to search"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum results"),
    scene_filter: Optional[str] = Query(None, description="Filter by scene: food, interior, exterior, view")
):
    """
    🖼️ Search places by uploading an image
    
    Upload a photo to find similar places. Uses SigLIP vision embeddings
    for semantic image matching.
    
    **Scene filters:**
    - `food` - Food/dish photos
    - `interior` - Inside shots  
    - `exterior` - Outside/facade shots
    - `view` - Scenic views
    - Leave empty for all scenes
    
    **Use cases:**
    - "Find a cafe that looks like this"
    - "Where can I get food like in this photo?"
    - "Find places with similar views"
    """
    try:
        # Read image bytes
        image_bytes = await image.read()
        
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Get image service
        img_service = get_image_service()
        
        # Search
        results = img_service.search_by_bytes(
            image_bytes=image_bytes,
            max_results=max_results,
            scene_filter=scene_filter
        )
        
        return ImageSearchResponse(
            results=[
                ImageSearchResult(
                    place_id=r.place_id,
                    name=r.name,
                    category=r.category,
                    rating=r.rating,
                    similarity=r.similarity,
                    matched_images=r.matched_images,
                    scene_type=r.scene_type
                ) for r in results
            ],
            total=len(results),
            scene_filter=scene_filter
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image search error: {str(e)}")


# ============================================================================
# Place Details Endpoints (Neo4j - Graph Database)
# ============================================================================

@app.get("/places/{place_id}", response_model=PlaceDetailsResponse, tags=["Places"])
async def get_place_details(
    place_id: str,
    include_nearby: bool = Query(True, description="Include nearby places"),
    include_related: bool = Query(True, description="Include same-category places"),
    nearby_limit: int = Query(5, ge=1, le=20, description="Max nearby places")
):
    """
    📍 Get complete place details from Neo4j
    
    Returns all place information including:
    - Basic info (name, address, rating, etc.)
    - Photos and reviews
    - Nearby places (using graph relationships)
    - Similar places in same category
    
    **Use after search to get full details before displaying to user.**
    """
    try:
        neo4j = get_neo4j_service()
        details = neo4j.get_place_with_enrichment(
            place_id=place_id,
            include_nearby=include_nearby,
            include_same_category=include_related,
            nearby_limit=nearby_limit
        )
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Place not found: {place_id}")
        
        return PlaceDetailsResponse(
            place_id=details.place_id,
            name=details.name,
            category=details.category,
            rating=details.rating,
            address=details.address,
            phone=details.phone,
            website=details.website,
            google_maps_url=details.google_maps_url,
            description=details.description,
            specialty=details.specialty,
            price_range=details.price_range,
            coordinates=CoordinatesModel(
                lat=details.coordinates['lat'],
                lng=details.coordinates['lng']
            ),
            photos_count=details.photos_count,
            reviews_count=details.reviews_count,
            photos=details.photos,
            reviews=[
                ReviewModel(text=r.text, rating=r.rating, reviewer=r.reviewer)
                for r in details.reviews
            ],
            nearby_places=[
                NearbyPlaceModel(
                    place_id=n.place_id,
                    name=n.name,
                    category=n.category,
                    rating=n.rating,
                    distance_km=n.distance_km
                ) for n in details.nearby_places
            ],
            same_category=details.same_category
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {str(e)}")


@app.get("/places/{place_id}/nearby", tags=["Places"])
async def get_nearby_places(
    place_id: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum results"),
    max_distance: float = Query(2.0, ge=0.1, le=10, description="Max distance in km")
):
    """
    📍 Get places near a specific place
    
    Uses Neo4j NEAR relationships for fast lookup.
    Results are sorted by distance.
    """
    try:
        neo4j = get_neo4j_service()
        nearby = neo4j.get_nearby_places(
            place_id=place_id,
            limit=limit,
            max_distance_km=max_distance
        )
        
        return {
            "place_id": place_id,
            "nearby_places": [
                {
                    "place_id": p.place_id,
                    "name": p.name,
                    "category": p.category,
                    "rating": p.rating,
                    "distance_km": p.distance_km
                } for p in nearby
            ],
            "total": len(nearby)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {str(e)}")


# ============================================================================
# System Endpoints
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    neo4j_status = "unknown"
    try:
        neo4j = get_neo4j_service()
        neo4j_status = "connected"
    except:
        neo4j_status = "disconnected"
    
    return {
        "status": "healthy",
        "service": "da-nang-rag-api",
        "version": "2.0.0",
        "components": {
            "rag_service": "connected",
            "neo4j_service": neo4j_status
        }
    }


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    rag_service.close()
    if neo4j_service:
        neo4j_service.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
