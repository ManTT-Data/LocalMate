"""
RAG Pipeline Configuration
Full-featured setup with multi-embedding and hybrid search
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PLACES_DIR = DATA_DIR / "places"
PHOTOS_DIR = DATA_DIR / "photos"
RAG_PROCESSED_DIR = DATA_DIR / "rag_processed"
RAG_PROCESSED_DIR.mkdir(exist_ok=True)

# ============================================================================
# SUPABASE
# ============================================================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # anon key for client

# Note: Supabase is only needed for upload step, not for extraction/embedding

# ============================================================================
# NEO4J (for data extraction)
# ============================================================================
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# ============================================================================
# EMBEDDING MODELS
# ============================================================================

# Google Text Embeddings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TEXT_EMBEDDING_MODEL = "models/text-embedding-004"
TEXT_EMBEDDING_DIM = 768
TEXT_BATCH_SIZE = 100  # Google allows batch processing

# SigLIP Image Embeddings (SOTA for zero-shot retrieval)
SIGLIP_MODEL_NAME = "google/siglip-base-patch16-256"  # ViT-B-16-SigLIP
# Alternative: "google/siglip-large-patch16-256" for ViT-L-16-SigLIP (better but slower)
IMAGE_EMBEDDING_DIM = 768  # SigLIP-base output dimension
IMAGE_BATCH_SIZE = 32  # GPU batch size

# ============================================================================
# LLM (optional enhancement)
# ============================================================================
USE_LLM_ENHANCEMENT = True  # Enable for best quality
LLM_MODEL = "gemini-2.0-flash"  # Fast and accurate
LLM_TOP_PLACES_COUNT = 303  # Enhance ALL places (303 total)

# ============================================================================
# EMBEDDING TYPES & WEIGHTS
# ============================================================================

# Text embedding types to generate per place
TEXT_EMBEDDING_TYPES = {
    "master": {
        "weight": 1.0,
        "description": "Full consolidated summary",
        "always_generate": True
    },
    "category_food": {
        "weight": 1.2,
        "description": "Food-focused description",
        "condition": lambda p: any(cat in p.get("category", "").lower() 
                                  for cat in ["restaurant", "bistro", "cafe", "food"])
    },
    "ambiance": {
        "weight": 1.0,
        "description": "Vibe, mood, atmosphere",
        "always_generate": True
    },
    "practical": {
        "weight": 0.8,
        "description": "Price, location, hours, parking",
        "always_generate": True
    },
    "reviews_positive": {
        "weight": 0.9,
        "description": "Aggregated positive reviews",
        "condition": lambda p: len(p.get("reviews", [])) >= 3
    },
    "llm_enhanced": {
        "weight": 1.3,
        "description": "LLM-generated summary (premium)",
        "condition": lambda p: p.get("rating", 0) >= 4.0
    }
}

# Image scene types
IMAGE_SCENE_TYPES = ["exterior", "interior", "food", "view", "people", "other"]

# Fusion weights for hybrid search
FUSION_WEIGHTS = {
    "text_master": 1.0,
    "text_category": 1.2,
    "text_ambiance": 1.0,
    "text_practical": 0.8,
    "text_reviews": 0.9,
    "text_llm": 1.3,
    "image": 1.1
}

# ============================================================================
# SEARCH PARAMETERS
# ============================================================================
DEFAULT_MATCH_THRESHOLD = 0.5  # Cosine similarity threshold
DEFAULT_MATCH_COUNT = 10
MAX_DISTANCE_KM = 5.0  # For location-based filtering
RRF_K = 60  # Reciprocal Rank Fusion constant

# ============================================================================
# CATEGORIES & KEYWORDS
# ============================================================================

FOOD_CATEGORIES = [
    "restaurant", "bistro", "cafe", "coffee", "food", 
    "bakery", "eatery", "diner", "tiffin"
]

# Intent classification keywords
INTENT_KEYWORDS = {
    "food": [
        "phở", "bánh", "cơm", "bún", "món", "ăn", "ngon", 
        "hải sản", "lẩu", "nướng", "quán", "nhà hàng"
    ],
    "ambiance": [
        "view", "đẹp", "chill", "yên tĩnh", "sang trọng", 
        "romantic", "lãng mạn", "không gian", "vibe", 
        "vintage", "hiện đại", "cozy"
    ],
    "practical": [
        "giá", "rẻ", "bao nhiêu", "tiền", "parking", 
        "đỗ xe", "gần", "xa", "mở cửa", "giờ"
    ],
    "location": [
        "biển", "trung tâm", "chợ", "downtown", "gần tôi",
        "quanh đây", "khu vực", "đường"
    ]
}

# Budget inference
BUDGET_KEYWORDS = {
    "low": ["rẻ", "sinh viên", "bình dân", "dưới 50k", "tiết kiệm"],
    "medium": ["trung bình", "vừa phải", "50k-100k"],
    "high": ["sang", "cao cấp", "luxury", "đắt", "premium"]
}

# ============================================================================
# PROCESSING FLAGS
# ============================================================================
SKIP_EXISTING_EMBEDDINGS = True  # Don't re-generate if already exists
PARALLEL_PROCESSING = True  # Use multiprocessing
MAX_WORKERS = 4  # CPU cores for parallel processing

# ============================================================================
# VALIDATION
# ============================================================================
assert GOOGLE_API_KEY, "Google API key missing for embeddings"

print("✅ RAG Configuration loaded successfully")
print(f"📁 Data directory: {DATA_DIR}")
print(f"🎯 Will generate {len(TEXT_EMBEDDING_TYPES)} text embedding types per place")
print(f"🖼️ Image embeddings: SigLIP {SIGLIP_MODEL_NAME}")
print(f"🤖 LLM enhancement: {'Enabled' if USE_LLM_ENHANCEMENT else 'Disabled'}")
if SUPABASE_URL:
    print(f"✅ Supabase configured")
else:
    print(f"⚠️ Supabase not configured (only needed for upload step)")
