"""
Upload embeddings and metadata to Supabase
"""

import asyncio
import pickle
import json
from typing import List
from supabase import create_client, Client
from tqdm import tqdm

from .models import TextEmbedding, ImageEmbedding
from .config import (
    SUPABASE_URL, SUPABASE_KEY,
    RAG_PROCESSED_DIR
)


class SupabaseUploader:
    """Upload embeddings to Supabase"""
    
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Connected to Supabase: {SUPABASE_URL[:40]}...")
    
    async def upload_text_embeddings(
        self, 
        embeddings: List[TextEmbedding] = None,
        batch_size: int = 100
    ):
        """Upload text embeddings in batches"""
        if embeddings is None:
            # Load from pickle
            with open(RAG_PROCESSED_DIR / "text_embeddings.pkl", 'rb') as f:
                embeddings = pickle.load(f)
        
        print(f"\n📝 Uploading {len(embeddings)} text embeddings...")
        
        # Clear existing data
        self.client.table('place_text_embeddings').delete().neq('id', '').execute()
        print("🗑️ Cleared existing text embeddings")
        
        # Upload in batches
        for i in tqdm(range(0, len(embeddings), batch_size), desc="Uploading text"):
            batch = embeddings[i:i + batch_size]
            
            # Convert to dicts
            rows = []
            for emb in batch:
                rows.append({
                    'place_id': emb.place_id,
                    'embedding_type': emb.embedding_type,
                    'embedding': emb.embedding.tolist(),
                    'source_text': emb.source_text[:2000] if emb.source_text else None,  # Limit text size
                    'metadata': emb.metadata
                })
            
            try:
                self.client.table('place_text_embeddings').insert(rows).execute()
            except Exception as e:
                print(f"  ⚠️ Batch {i//batch_size} failed: {e}")
        
        print(f"✅ Uploaded {len(embeddings)} text embeddings")
    
    async def upload_image_embeddings(
        self, 
        embeddings: List[ImageEmbedding] = None,
        batch_size: int = 100
    ):
        """Upload image embeddings in batches"""
        if embeddings is None:
            # Load from pickle
            with open(RAG_PROCESSED_DIR / "image_embeddings.pkl", 'rb') as f:
                embeddings = pickle.load(f)
        
        print(f"\n🖼️ Uploading {len(embeddings)} image embeddings...")
        
        # Clear existing data
        self.client.table('place_image_embeddings').delete().neq('id', '').execute()
        print("🗑️ Cleared existing image embeddings")
        
        # Upload in batches
        for i in tqdm(range(0, len(embeddings), batch_size), desc="Uploading images"):
            batch = embeddings[i:i + batch_size]
            
            rows = []
            for emb in batch:
                rows.append({
                    'place_id': emb.place_id,
                    'image_url': emb.image_url,
                    'embedding': emb.embedding.tolist(),
                    'scene_type': emb.scene_type,
                    'metadata': emb.metadata
                })
            
            try:
                self.client.table('place_image_embeddings').insert(rows).execute()
            except Exception as e:
                print(f"  ⚠️ Batch {i//batch_size} failed: {e}")
        
        print(f"✅ Uploaded {len(embeddings)} image embeddings")
    
    async def upload_metadata(self, places_file: str = None, batch_size: int = 100):
        """Upload places metadata"""
        if places_file is None:
            places_file = RAG_PROCESSED_DIR / "places_normalized.json"
        
        with open(places_file, 'r', encoding='utf-8') as f:
            places = json.load(f)
        
        print(f"\n📋 Uploading metadata for {len(places)} places...")
        
        # Clear existing
        self.client.table('places_metadata').delete().neq('place_id', '').execute()
        print("🗑️ Cleared existing metadata")
        
        for i in tqdm(range(0, len(places), batch_size), desc="Uploading metadata"):
            batch = places[i:i + batch_size]
            
            rows = []
            for place in batch:
                coords = place.get('coordinates', {})
                lat = coords.get('latitude', 0)
                lng = coords.get('longitude', 0)
                
                rows.append({
                    'place_id': place.get('id'),
                    'name': place.get('name'),
                    'name_vi': place.get('name_vi'),
                    'category': place.get('category'),
                    'address': place.get('address'),
                    'rating': place.get('rating'),
                    'price_min': place.get('price_min'),
                    'price_max': place.get('price_max'),
                    'tags': place.get('tags', []),
                    'coordinates': f'POINT({lng} {lat})' if lat and lng else None,
                    'raw_data': {
                        'phone': place.get('phone'),
                        'website': place.get('website'),
                        'google_maps_url': place.get('google_maps_url'),
                        'description': place.get('description'),
                        'specialty': place.get('specialty'),
                        'photos_count': place.get('photos_count'),
                        'reviews_count': place.get('reviews_count')
                    }
                })
            
            try:
                self.client.table('places_metadata').insert(rows).execute()
            except Exception as e:
                print(f"  ⚠️ Batch {i//batch_size} failed: {e}")
        
        print(f"✅ Uploaded metadata for {len(places)} places")
    
    async def upload_all(self):
        """Upload everything"""
        print("="*60)
        print("🚀 UPLOADING TO SUPABASE")
        print("="*60)
        
        await self.upload_metadata()
        await self.upload_text_embeddings()
        await self.upload_image_embeddings()
        
        print("\n" + "="*60)
        print("✅ ALL UPLOADS COMPLETE!")
        print("="*60)
        
        # Verify counts
        text_count = self.client.table('place_text_embeddings').select('id', count='exact').execute()
        image_count = self.client.table('place_image_embeddings').select('id', count='exact').execute()
        meta_count = self.client.table('places_metadata').select('place_id', count='exact').execute()
        
        print(f"\n📊 Final counts:")
        print(f"  📝 Text embeddings: {text_count.count}")
        print(f"  🖼️ Image embeddings: {image_count.count}")
        print(f"  📋 Places metadata: {meta_count.count}")


async def main():
    """Upload all data to Supabase"""
    uploader = SupabaseUploader()
    await uploader.upload_all()


if __name__ == "__main__":
    asyncio.run(main())
