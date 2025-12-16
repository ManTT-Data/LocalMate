"""
Generate text embeddings using Google Gemini API
Batch processing with rate limiting
"""

import asyncio
import time
import pickle
from typing import List, Dict
import numpy as np
import google.generativeai as genai
from tqdm import tqdm

from .models import PlaceData, TextEmbedding
from .text_converter import TextConverter
from .config import (
    GOOGLE_API_KEY, TEXT_EMBEDDING_MODEL, TEXT_BATCH_SIZE,
    RAG_PROCESSED_DIR, USE_LLM_ENHANCEMENT
)

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)


class EmbeddingGenerator:
    """Generate text embeddings for places"""
    
    def __init__(self):
        self.embedding_model = TEXT_EMBEDDING_MODEL
        self.batch_size = TEXT_BATCH_SIZE
        self.rate_limit_delay = 0.1  # seconds between batches
    
    async def generate_for_places(
        self, 
        places: List[PlaceData],
        output_file: str = "text_embeddings.pkl"
    ) -> List[TextEmbedding]:
        """
        Generate all text embeddings for all places
        Returns list of TextEmbedding objects
        """
        all_embeddings = []
        
        print(f"\n🔄 Generating embeddings for {len(places)} places...")
        print(f"📊 Embedding types: {list(TextConverter.generate_all_texts(places[0]).keys())}")
        
        for i, place in enumerate(tqdm(places, desc="Processing places")):
            place_embeddings = await self._generate_for_single_place(place)
            all_embeddings.extend(place_embeddings)
            
            # Progress update
            if (i + 1) % 10 == 0:
                print(f"  ✓ Processed {i + 1}/{len(places)} places, {len(all_embeddings)} embeddings total")
        
        # Save to pickle
        output_path = RAG_PROCESSED_DIR / output_file
        with open(output_path, 'wb') as f:
            pickle.dump(all_embeddings, f)
        
        print(f"\n✅ Generated {len(all_embeddings)} embeddings")
        print(f"💾 Saved to {output_path}")
        
        return all_embeddings
    
    async def _generate_for_single_place(self, place: PlaceData) -> List[TextEmbedding]:
        """Generate all embedding types for a single place"""
        embeddings = []
        
        # 1. Generate all text types (template-based)
        texts = TextConverter.generate_all_texts(place)
        
        # 2. Optionally add LLM-enhanced text
        if USE_LLM_ENHANCEMENT:
            try:
                llm_text = await TextConverter.to_llm_enhanced(place)
                texts['llm_enhanced'] = llm_text
            except Exception as e:
                print(f"  ⚠️ LLM enhancement failed for {place.id}: {e}")
        
        # 3. Batch embed all texts
        text_list = list(texts.values())
        type_list = list(texts.keys())
        
        try:
            vectors = await self._batch_embed(text_list)
            
            # Create TextEmbedding objects
            for emb_type, text, vector in zip(type_list, text_list, vectors):
                embeddings.append(TextEmbedding(
                    place_id=place.id,
                    embedding_type=emb_type,
                    source_text=text,
                    embedding=vector,
                    metadata={
                        'place_name': place.name,
                        'category': place.category,
                        'rating': place.rating
                    }
                ))
        except Exception as e:
            print(f"  ❌ Embedding failed for {place.id}: {e}")
        
        return embeddings
    
    async def _batch_embed(self, texts: List[str]) -> List[np.ndarray]:
        """
        Batch embed texts using Gemini API
        Handles rate limiting automatically
        """
        vectors = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Embed batch
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=batch,
                    task_type="retrieval_document"
                )
                
                # Extract vectors
                for embedding in result['embedding']:
                    vectors.append(np.array(embedding, dtype=np.float32))
                
                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                print(f"  ⚠️ Batch embedding error: {e}")
                # Retry with smaller batch or individual items
                for text in batch:
                    try:
                        result = genai.embed_content(
                            model=self.embedding_model,
                            content=text,
                            task_type="retrieval_document"
                        )
                        vectors.append(np.array(result['embedding'], dtype=np.float32))
                        await asyncio.sleep(0.2)  # Longer delay for individual requests
                    except Exception as e2:
                        print(f"  ❌ Individual embedding failed: {e2}")
                        # Use zero vector as fallback
                        vectors.append(np.zeros(768, dtype=np.float32))
        
        return vectors
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single user query
        Synchronous version for API usage
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"  # Different task type for queries
            )
            return np.array(result['embedding'], dtype=np.float32)
        except Exception as e:
            print(f"❌ Query embedding failed: {e}")
            return np.zeros(768, dtype=np.float32)
    
    def load_embeddings(self, file_path: str = None) -> List[TextEmbedding]:
        """Load embeddings from pickle file"""
        if file_path is None:
            file_path = RAG_PROCESSED_DIR / "text_embeddings.pkl"
        
        with open(file_path, 'rb') as f:
            embeddings = pickle.load(f)
        
        print(f"✅ Loaded {len(embeddings)} embeddings from {file_path}")
        return embeddings


async def main():
    """Test embedding generation"""
    import json
    
    # Load places
    places_file = RAG_PROCESSED_DIR / "places_normalized.json"
    if not places_file.exists():
        print("❌ Run extract_places.py first!")
        return
    
    with open(places_file, 'r', encoding='utf-8') as f:
        places_data = json.load(f)
    
    # Convert to PlaceData objects (first 5 for testing)
    from .extract_places import PlaceExtractor
    extractor = PlaceExtractor()
    places = [extractor._json_to_place_data(p) for p in places_data[:5]]
    places = [p for p in places if p]  # Filter None
    
    print(f"📊 Testing with {len(places)} places")
    
    # Generate embeddings
    generator = EmbeddingGenerator()
    embeddings = await generator.generate_for_places(places, output_file="test_embeddings.pkl")
    
    print(f"\n✅ Generated {len(embeddings)} embeddings")
    print(f"📊 Embeddings per place: {len(embeddings) / len(places):.1f}")
    
    # Test query embedding
    query = "quán cafe view đẹp"
    query_vec = generator.embed_query(query)
    print(f"\n🔍 Query embedding shape: {query_vec.shape}")


if __name__ == "__main__":
    asyncio.run(main())
