"""
Data models for RAG pipeline
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import numpy as np


@dataclass
class Coordinates:
    """Geographic coordinates"""
    latitude: float
    longitude: float
    
    def to_postgis_point(self) -> str:
        """Convert to PostGIS POINT format"""
        return f"POINT({self.longitude} {self.latitude})"


@dataclass
class Review:
    """Place review"""
    rating: int
    reviewer: str
    text: str
    
    def __post_init__(self):
        # Clean text
        self.text = self.text.strip() if self.text else ""


@dataclass
class Photo:
    """Place photo metadata"""
    path: str
    filename: str
    order: int
    
    def get_full_path(self, base_dir: str) -> str:
        """Get absolute path"""
        from pathlib import Path
        return str(Path(base_dir) / self.path)


@dataclass
class NearbyPlace:
    """Nearby place reference"""
    distance_km: float
    name: str
    rating: float
    category: str


@dataclass
class PlaceData:
    """Complete place data extracted from source"""
    id: str
    name: str
    name_vi: Optional[str]
    rating: float
    category: str
    category_name: str
    address: str
    coordinates: Coordinates
    phone: Optional[str]
    website: Optional[str]
    google_maps_url: str
    price_range: Optional[str]
    description: str
    specialty: str
    photos_count: int
    reviews_count: int
    photos: List[Photo]
    reviews: List[Review]
    nearby_places: List[NearbyPlace] = field(default_factory=list)
    
    # Extracted attributes (computed)
    tags: List[str] = field(default_factory=list)
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    
    def __post_init__(self):
        """Post-process data"""
        # Parse price range
        if self.price_range:
            self._parse_price_range()
        
        # Extract tags
        self._extract_tags()
    
    def _parse_price_range(self):
        """Extract min/max price from price_range string"""
        import re
        # Example: "40,000 - 80,000" or "25,000 - 45,000 VND"
        numbers = re.findall(r'[\d,]+', self.price_range)
        if len(numbers) >= 2:
            try:
                self.price_min = float(numbers[0].replace(',', ''))
                self.price_max = float(numbers[1].replace(',', ''))
            except ValueError:
                pass
        elif len(numbers) == 1:
            try:
                price = float(numbers[0].replace(',', ''))
                self.price_min = price
                self.price_max = price
            except ValueError:
                pass
    
    def _extract_tags(self):
        """Extract searchable tags from various fields"""
        tags = set()
        
        # Category-based tags
        category_lower = self.category.lower()
        if any(word in category_lower for word in ['cafe', 'coffee']):
            tags.add('cafe')
        if any(word in category_lower for word in ['restaurant', 'food', 'bistro']):
            tags.add('restaurant')
        if 'hotel' in category_lower:
            tags.add('hotel')
        if 'bar' in category_lower:
            tags.add('bar')
        
        # Price-based tags
        if self.price_max and self.price_max < 50000:
            tags.add('budget')
        elif self.price_min and self.price_min > 200000:
            tags.add('premium')
        
        # Review-based tags (from description and reviews)
        text_combined = f"{self.description} {self.specialty}".lower()
        for review in self.reviews[:5]:
            text_combined += f" {review.text.lower()}"
        
        if any(word in text_combined for word in ['view', 'đẹp', 'cảnh']):
            tags.add('scenic_view')
        if any(word in text_combined for word in ['parking', 'đỗ xe']):
            tags.add('parking')
        if any(word in text_combined for word in ['wifi', 'internet']):
            tags.add('wifi')
        if any(word in text_combined for word in ['outdoor', 'ngoài trời']):
            tags.add('outdoor_seating')
        if any(word in text_combined for word in ['romantic', 'lãng mạn']):
            tags.add('romantic')
        if any(word in text_combined for word in ['family', 'gia đình']):
            tags.add('family_friendly')
        
        self.tags = list(tags)
    
    def to_metadata_dict(self) -> Dict[str, Any]:
        """Convert to Supabase metadata format"""
        return {
            "place_id": self.id,
            "name": self.name,
            "category": self.category,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "rating": self.rating,
            "coordinates": self.coordinates.to_postgis_point(),
            "tags": self.tags,
            "raw_data": {
                "name_vi": self.name_vi,
                "address": self.address,
                "phone": self.phone,
                "website": self.website,
                "google_maps_url": self.google_maps_url,
                "description": self.description,
                "specialty": self.specialty,
                "photos_count": self.photos_count,
                "reviews_count": self.reviews_count
            }
        }


@dataclass
class TextEmbedding:
    """Text embedding with metadata"""
    place_id: str
    embedding_type: str
    source_text: str
    embedding: np.ndarray  # Shape: (768,)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_supabase_dict(self) -> Dict[str, Any]:
        """Convert to Supabase insert format"""
        return {
            "place_id": self.place_id,
            "embedding_type": self.embedding_type,
            "source_text": self.source_text,
            "embedding": self.embedding.tolist(),
            "metadata": self.metadata
        }


@dataclass
class ImageEmbedding:
    """Image embedding with metadata"""
    place_id: str
    image_url: str  # Relative or absolute path
    embedding: np.ndarray  # Shape: (512,) for CLIP
    scene_type: str  # "interior", "exterior", "food", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_supabase_dict(self) -> Dict[str, Any]:
        """Convert to Supabase insert format"""
        return {
            "place_id": self.place_id,
            "image_url": self.image_url,
            "embedding": self.embedding.tolist(),
            "scene_type": self.scene_type,
            "metadata": self.metadata
        }


@dataclass
class SearchQuery:
    """User search query"""
    text: Optional[str] = None
    image_bytes: Optional[bytes] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    gps_coords: Optional[Coordinates] = None
    max_results: int = 10
    
    def has_text(self) -> bool:
        return bool(self.text)
    
    def has_image(self) -> bool:
        return bool(self.image_bytes)
    
    def is_hybrid(self) -> bool:
        return self.has_text() and self.has_image()


@dataclass
class SearchResult:
    """Search result with score and explanation"""
    place_id: str
    name: str
    category: str
    similarity_score: float
    source_embeddings: List[str]  # Which embedding types matched
    metadata: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[str] = None  # LLM-generated explanation
    
    def __lt__(self, other):
        """For sorting by score"""
        return self.similarity_score < other.similarity_score


@dataclass
class ConversationContext:
    """Multi-turn conversation state"""
    session_id: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    accumulated_filters: Dict[str, Any] = field(default_factory=dict)
    last_results: List[SearchResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_turn(self, query: str, results: List[SearchResult]):
        """Add conversation turn"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": len(results),
            "top_result": results[0].place_id if results else None
        })
        self.last_results = results
    
    def update_filters(self, new_filters: Dict[str, Any]):
        """Progressive filtering"""
        self.accumulated_filters.update(new_filters)
