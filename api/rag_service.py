"""
RAG Search Service - Optimized Version
Vector search with category boosting, reranking, and LLM explanations
"""

import os
import json
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from urllib.parse import quote_plus
import google.generativeai as genai
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-1-ap-northeast-2.pooler.supabase.com")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres.skrydftiwenxrxdxesor")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not SUPABASE_DB_PASSWORD:
    raise ValueError("Missing SUPABASE_DB_PASSWORD in environment variables")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment variables")

# Build database URL
PASSWORD = quote_plus(SUPABASE_DB_PASSWORD)
DATABASE_URL = f"postgresql://{SUPABASE_DB_USER}:{PASSWORD}@{SUPABASE_DB_HOST}:5432/postgres"

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)



@dataclass
class SearchResult:
    """Search result item"""
    place_id: str
    name: str
    category: str
    rating: float
    similarity: float
    description: str
    source_types: List[str] = field(default_factory=list)
    llm_text: str = ""
    explanation: Optional[str] = None


class RAGSearchService:
    """Optimized vector-based search for place recommendations"""
    
    # Category mappings for query intent
    CATEGORY_KEYWORDS = {
        'cafe': ['cafe', 'cà phê', 'coffee', 'caphe'],
        'pho': ['phở', 'pho'],
        'banh_mi': ['bánh mì', 'banh mi', 'bread'],
        'seafood': ['hải sản', 'hai san', 'seafood', 'cá', 'tôm', 'cua'],
        'restaurant': ['nhà hàng', 'restaurant', 'quán ăn'],
        'bar': ['bar', 'pub', 'cocktail', 'beer', 'bia'],
        'hotel': ['hotel', 'khách sạn', 'resort', 'villa']
    }
    
    CATEGORY_TO_DB = {
        'cafe': ['Coffee shop', 'Cafe', 'Coffee house'],
        'pho': ['Pho restaurant', 'Bistro', 'Restaurant'],
        'banh_mi': ['Bakery', 'Tiffin center', 'Restaurant'],
        'seafood': ['Seafood restaurant', 'Restaurant', 'Asian restaurant'],
        'restaurant': ['Restaurant', 'Vietnamese restaurant', 'Asian restaurant'],
        'bar': ['Bar', 'Cocktail bar', 'Pub', 'Night club'],
        'hotel': ['Hotel', 'Resort', 'Apartment', 'Villa']
    }
    
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected to Supabase PostgreSQL")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed text query using Gemini"""
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query"
        )
        return np.array(result['embedding'], dtype=np.float32)
    
    def detect_category_intent(self, query: str) -> Optional[str]:
        """Detect if query is asking for specific category"""
        query_lower = query.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                return category
        return None
    
    def search_text(
        self, 
        query: str, 
        max_results: int = 10,
        rating_min: float = None
    ) -> List[SearchResult]:
        """
        Optimized text search with:
        1. Multi-embedding search (llm_enhanced priority)
        2. Category boosting
        3. Similarity reranking
        """
        # 1. Embed query
        query_embedding = self.embed_text(query)
        
        # 2. Detect category intent
        category_intent = self.detect_category_intent(query)
        category_filter = self.CATEGORY_TO_DB.get(category_intent, []) if category_intent else []
        
        # 3. Search all relevant embedding types
        content_types = ['llm_enhanced', 'master', 'category_food', 'ambiance', 'reviews_positive']
        
        all_matches = []
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Single optimized query
            sql = """
                WITH ranked_results AS (
                    SELECT 
                        e.place_id,
                        e.content_type,
                        e.source_text,
                        1 - (e.embedding <=> %s::vector) as similarity,
                        m.name,
                        m.category,
                        m.rating,
                        m.raw_data,
                        ROW_NUMBER() OVER (
                            PARTITION BY e.place_id, e.content_type 
                            ORDER BY e.embedding <=> %s::vector
                        ) as rn
                    FROM place_text_embeddings e
                    JOIN places_metadata m ON e.place_id = m.place_id
                    WHERE e.content_type = ANY(%s)
                      AND m.name IS NOT NULL 
                      AND m.name != 'Unknown'
                      AND m.name != 'Results'
                      AND m.name != ''
                )
                SELECT * FROM ranked_results
                WHERE rn = 1 AND similarity > 0.25
                ORDER BY similarity DESC
                LIMIT 100
            """
            
            cur.execute(sql, [
                query_embedding.tolist(),
                query_embedding.tolist(),
                content_types
            ])
            
            results = cur.fetchall()
        
        # 4. Process and score results
        place_scores = defaultdict(lambda: {
            'vector_score': 0.0,
            'category_boost': 0.0,
            'rating_boost': 0.0,
            'types': set(),
            'data': None,
            'llm_text': ''
        })
        
        for r in results:
            pid = r['place_id']
            similarity = float(r['similarity'])
            emb_type = r['content_type']
            
            # Store best similarity per type
            type_weight = {
                'llm_enhanced': 1.5,  # Highest quality
                'master': 1.0,
                'category_food': 0.8,
                'ambiance': 0.7,
                'reviews_positive': 0.6
            }.get(emb_type, 0.5)
            
            weighted_sim = similarity * type_weight
            place_scores[pid]['vector_score'] = max(
                place_scores[pid]['vector_score'], 
                weighted_sim
            )
            place_scores[pid]['types'].add(emb_type)
            
            # Store LLM text if available
            if emb_type == 'llm_enhanced' and r['source_text']:
                place_scores[pid]['llm_text'] = r['source_text']
            
            if place_scores[pid]['data'] is None:
                place_scores[pid]['data'] = r
            
            # Category boost
            if category_filter and r['category'] in category_filter:
                place_scores[pid]['category_boost'] = 0.15  # 15% boost
            
            # Rating boost
            if r['rating'] and r['rating'] >= 4.5:
                place_scores[pid]['rating_boost'] = 0.05
            elif r['rating'] and r['rating'] >= 4.0:
                place_scores[pid]['rating_boost'] = 0.02
        
        # 5. Calculate final scores
        scored_places = []
        for pid, scores in place_scores.items():
            final_score = (
                scores['vector_score'] + 
                scores['category_boost'] + 
                scores['rating_boost'] +
                len(scores['types']) * 0.01  # Small bonus for multi-type match
            )
            scored_places.append((pid, final_score, scores))
        
        # 6. Sort and return top results
        scored_places.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for pid, score, scores in scored_places[:max_results]:
            data = scores['data']
            
            # Skip if rating filter
            if rating_min and data['rating'] and data['rating'] < rating_min:
                continue
            
            results.append(SearchResult(
                place_id=pid,
                name=data['name'],
                category=data['category'],
                rating=float(data['rating']) if data['rating'] else 0,
                similarity=score,
                description=data['raw_data'].get('description', '') if data['raw_data'] else '',
                source_types=list(scores['types']),
                llm_text=scores['llm_text'][:300] if scores['llm_text'] else ''
            ))
        
        return results
    
    def search_by_category(
        self,
        category: str,
        query_context: str = None,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Direct category-based search with optional semantic ranking"""
        
        db_categories = self.CATEGORY_TO_DB.get(category, [category])
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            if query_context:
                # Semantic ranking within category
                query_embedding = self.embed_text(query_context)
                
                sql = """
                    SELECT DISTINCT ON (e.place_id)
                        e.place_id,
                        e.source_text,
                        1 - (e.embedding <=> %s::vector) as similarity,
                        m.name,
                        m.category,
                        m.rating,
                        m.raw_data
                    FROM place_text_embeddings e
                    JOIN places_metadata m ON e.place_id = m.place_id
                    WHERE m.category = ANY(%s)
                      AND e.content_type = 'llm_enhanced'
                      AND m.name IS NOT NULL AND m.name != 'Results'
                    ORDER BY e.place_id, e.embedding <=> %s::vector
                    LIMIT %s
                """
                cur.execute(sql, [
                    query_embedding.tolist(),
                    db_categories,
                    query_embedding.tolist(),
                    max_results * 2
                ])
            else:
                # Just by rating
                sql = """
                    SELECT 
                        m.place_id,
                        m.name,
                        m.category,
                        m.rating,
                        m.raw_data
                    FROM places_metadata m
                    WHERE m.category = ANY(%s)
                      AND m.name IS NOT NULL AND m.name != 'Results'
                    ORDER BY m.rating DESC NULLS LAST
                    LIMIT %s
                """
                cur.execute(sql, [db_categories, max_results])
            
            rows = cur.fetchall()
        
        results = []
        for r in rows[:max_results]:
            results.append(SearchResult(
                place_id=r['place_id'],
                name=r['name'],
                category=r['category'],
                rating=float(r['rating']) if r['rating'] else 0,
                similarity=float(r.get('similarity', 0)),
                description=r['raw_data'].get('description', '') if r.get('raw_data') else '',
                source_types=['category_filter']
            ))
        
        return results
    
    async def generate_explanation(
        self, 
        place: SearchResult, 
        query: str
    ) -> str:
        """Generate LLM explanation for recommendation"""
        prompt = f"""
Người dùng tìm: "{query}"
Địa điểm: {place.name} ({place.category})
Đánh giá: {place.rating}/5
Mô tả: {place.llm_text or place.description[:200] if place.description else 'N/A'}

Giải thích ngắn gọn (1-2 câu) tại sao địa điểm này phù hợp với yêu cầu.
Chỉ trả về phần giải thích, không thêm tiêu đề.
        """.strip()
        
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = await model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ Explanation generation failed: {e}")
            return ""
    
    def close(self):
        """Close database connection"""
        self.conn.close()


# Test
if __name__ == "__main__":
    service = RAGSearchService()
    
    print("\n" + "="*60)
    print("🧪 OPTIMIZED SEARCH TEST")
    print("="*60)
    
    test_queries = [
        ("quán cafe view đẹp", None),
        ("phở ngon", None),
        ("bánh mì sáng", None),
        ("nơi lãng mạn hẹn hò", None),
        ("quán ăn hải sản ngon", None),
        ("bar cocktail", None),
    ]
    
    for query, _ in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = service.search_text(query, max_results=5)
        
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Category: {r.category} | ⭐{r.rating} | Score: {r.similarity:.3f}")
            print(f"     Types: {r.source_types}")
            if r.llm_text:
                print(f"     LLM: {r.llm_text[:100]}...")
    
    # Test category search
    print("\n" + "="*60)
    print("🧪 CATEGORY SEARCH TEST")
    print("="*60)
    
    print("\n☕ Top Cafes:")
    cafes = service.search_by_category('cafe', 'view đẹp chill', max_results=5)
    for i, r in enumerate(cafes, 1):
        print(f"  {i}. {r.name} ({r.category}) ⭐{r.rating}")
    
    print("\n🍜 Top Pho:")
    pho = service.search_by_category('pho', 'ngon giá rẻ', max_results=5)
    for i, r in enumerate(pho, 1):
        print(f"  {i}. {r.name} ({r.category}) ⭐{r.rating}")
    
    service.close()
    print("\n✅ Test complete!")
