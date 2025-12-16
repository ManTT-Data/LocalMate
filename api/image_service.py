"""
Image Search Service - SigLIP-based image embedding and search
Provides image-to-place matching using vector similarity
"""

import os
import io
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
from urllib.parse import quote_plus
from PIL import Image
import torch
from dotenv import load_dotenv

load_dotenv()

# Database configuration
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-1-ap-northeast-2.pooler.supabase.com")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres.skrydftiwenxrxdxesor")

if not SUPABASE_DB_PASSWORD:
    raise ValueError("Missing SUPABASE_DB_PASSWORD in environment variables")

PASSWORD = quote_plus(SUPABASE_DB_PASSWORD)
DATABASE_URL = f"postgresql://{SUPABASE_DB_USER}:{PASSWORD}@{SUPABASE_DB_HOST}:5432/postgres"


@dataclass
class ImageSearchResult:
    """Image search result"""
    place_id: str
    name: str
    category: str
    rating: float
    similarity: float
    matched_images: int
    scene_type: str


class ImageSearchService:
    """Service for image-based place search using SigLIP embeddings"""
    
    def __init__(self):
        self.model = None
        self.preprocess = None
        self.device = None
        self.conn = None
        self._load_model()
        self._connect_db()
    
    def _load_model(self):
        """Load SigLIP model for image embedding"""
        try:
            import open_clip
            
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                "ViT-B-16-SigLIP", pretrained="webli"
            )
            self.model.eval()
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            print(f"✅ Loaded SigLIP model on {self.device}")
        except Exception as e:
            print(f"⚠️ Failed to load SigLIP model: {e}")
            raise
    
    def _connect_db(self):
        """Connect to Supabase PostgreSQL"""
        self.conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected to Supabase PostgreSQL for image search")
    
    def embed_image(self, image: Image.Image) -> np.ndarray:
        """
        Generate embedding for an image
        
        Args:
            image: PIL Image object
            
        Returns:
            Normalized embedding vector (768-dim)
        """
        # Ensure RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Preprocess and embed
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy()[0]
    
    def embed_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Generate embedding from image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Normalized embedding vector
        """
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        return self.embed_image(image)
    
    def search(
        self,
        image_embedding: np.ndarray,
        max_results: int = 10,
        scene_filter: Optional[str] = None,
        min_similarity: float = 0.2
    ) -> List[ImageSearchResult]:
        """
        Search for similar places using image embedding
        
        Args:
            image_embedding: Query image embedding
            max_results: Maximum number of places to return
            scene_filter: Filter by scene type (food, interior, exterior, view)
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of ImageSearchResult objects
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = """
                SELECT 
                    e.place_id,
                    COALESCE(e.metadata->>'scene_type', 'unknown') as scene_type,
                    e.image_url,
                    1 - (e.embedding <=> %s::vector) as similarity,
                    m.name,
                    m.category,
                    m.rating,
                    m.raw_data
                FROM place_image_embeddings e
                JOIN places_metadata m ON e.place_id = m.place_id
                WHERE 1 - (e.embedding <=> %s::vector) > %s
                  AND m.name IS NOT NULL 
                  AND m.name != 'Results'
                  AND m.name != ''
            """
            params = [image_embedding.tolist(), image_embedding.tolist(), min_similarity]
            
            if scene_filter and scene_filter.lower() != "all":
                sql += " AND e.metadata->>'scene_type' = %s"
                params.append(scene_filter)
            
            sql += " ORDER BY e.embedding <=> %s::vector LIMIT 100"
            params.append(image_embedding.tolist())
            
            cur.execute(sql, params)
            rows = cur.fetchall()
        
        # Aggregate by place (multiple images per place)
        place_scores: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_score': 0.0,
            'count': 0,
            'data': None,
            'scene_types': set()
        })
        
        for r in rows:
            pid = r['place_id']
            place_scores[pid]['total_score'] += float(r['similarity'])
            place_scores[pid]['count'] += 1
            place_scores[pid]['scene_types'].add(r['scene_type'])
            if place_scores[pid]['data'] is None:
                place_scores[pid]['data'] = r
        
        # Sort by average similarity
        sorted_places = sorted(
            place_scores.items(),
            key=lambda x: x[1]['total_score'] / x[1]['count'],
            reverse=True
        )[:max_results]
        
        # Build results
        results = []
        for pid, data in sorted_places:
            r = data['data']
            avg_score = data['total_score'] / data['count']
            
            results.append(ImageSearchResult(
                place_id=pid,
                name=r['name'],
                category=r['category'] or '',
                rating=float(r['rating'] or 0),
                similarity=round(avg_score, 4),
                matched_images=data['count'],
                scene_type=list(data['scene_types'])[0] if data['scene_types'] else 'unknown'
            ))
        
        return results
    
    def search_by_image(
        self,
        image: Image.Image,
        max_results: int = 10,
        scene_filter: Optional[str] = None
    ) -> List[ImageSearchResult]:
        """
        Full pipeline: embed image and search
        
        Args:
            image: PIL Image
            max_results: Max results
            scene_filter: Filter by scene type
            
        Returns:
            List of matching places
        """
        embedding = self.embed_image(image)
        return self.search(embedding, max_results, scene_filter)
    
    def search_by_bytes(
        self,
        image_bytes: bytes,
        max_results: int = 10,
        scene_filter: Optional[str] = None
    ) -> List[ImageSearchResult]:
        """
        Full pipeline: embed image bytes and search
        
        Args:
            image_bytes: Raw image bytes
            max_results: Max results
            scene_filter: Filter by scene type
            
        Returns:
            List of matching places
        """
        embedding = self.embed_image_bytes(image_bytes)
        return self.search(embedding, max_results, scene_filter)
    
    def close(self):
        """Close connections"""
        if self.conn:
            self.conn.close()


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 IMAGE SEARCH SERVICE TEST")
    print("=" * 60)
    
    service = ImageSearchService()
    
    # Test with a sample query (just verify service works)
    print("\n✅ Service initialized successfully!")
    print(f"   Device: {service.device}")
    print(f"   Model loaded: {service.model is not None}")
    print(f"   DB connected: {service.conn is not None}")
    
    service.close()
    print("\n✅ Test complete!")
