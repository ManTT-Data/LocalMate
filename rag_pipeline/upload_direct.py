"""
Upload embeddings to Supabase using direct PostgreSQL connection
Uses psycopg2-binary for direct database access
"""

import os
import asyncio
import pickle
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm
import numpy as np
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Configuration from environment
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-1-ap-northeast-2.pooler.supabase.com")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres.skrydftiwenxrxdxesor")

if not SUPABASE_DB_PASSWORD:
    raise ValueError("Missing SUPABASE_DB_PASSWORD in environment variables")

PASSWORD = quote_plus(SUPABASE_DB_PASSWORD)
DATABASE_URL = f"postgresql://{SUPABASE_DB_USER}:{PASSWORD}@{SUPABASE_DB_HOST}:5432/postgres"
RAG_PROCESSED_DIR = Path(__file__).parent.parent / "data" / "rag_processed"



def get_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)


def setup_schema(conn):
    """Create tables and functions"""
    print("📦 Setting up database schema...")
    
    with conn.cursor() as cur:
        # Enable extensions
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("  ✓ vector extension enabled")
        except Exception as e:
            print(f"  ⚠️ vector extension: {e}")
        
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            print("  ✓ postgis extension enabled")
        except Exception as e:
            print(f"  ⚠️ postgis extension: {e}")
        
        # Create text embeddings table (matches existing schema)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS place_text_embeddings (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                place_id text NOT NULL,
                embedding vector(768),
                content_type text,
                source_text text,
                metadata jsonb DEFAULT '{}',
                created_at timestamptz DEFAULT now()
            );
        """)
        print("  ✓ place_text_embeddings table ready")
        
        # Create image embeddings table (matches existing schema)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS place_image_embeddings (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                place_id text NOT NULL,
                embedding vector(768),
                image_url text,
                metadata jsonb DEFAULT '{}',
                created_at timestamptz DEFAULT now()
            );
        """)
        print("  ✓ place_image_embeddings table ready")
        
        # Create metadata table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS places_metadata (
                place_id text PRIMARY KEY,
                name text NOT NULL,
                name_vi text,
                category text,
                address text,
                rating numeric,
                price_min numeric,
                price_max numeric,
                tags text[] DEFAULT '{}',
                coordinates geography(POINT),
                raw_data jsonb DEFAULT '{}',
                created_at timestamptz DEFAULT now(),
                updated_at timestamptz DEFAULT now()
            );
        """)
        print("  ✓ places_metadata table created")
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_text_place_id ON place_text_embeddings(place_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_text_content_type ON place_text_embeddings(content_type);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_image_place_id ON place_image_embeddings(place_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_meta_category ON places_metadata(category);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_meta_rating ON places_metadata(rating);")
        print("  ✓ Indexes created")
        
        conn.commit()
        print("✅ Schema setup complete!")


def upload_text_embeddings(conn, batch_size=50):
    """Upload text embeddings"""
    pkl_file = RAG_PROCESSED_DIR / "text_embeddings.pkl"
    
    with open(pkl_file, 'rb') as f:
        embeddings = pickle.load(f)
    
    print(f"\n📝 Uploading {len(embeddings)} text embeddings...")
    
    with conn.cursor() as cur:
        # Clear existing
        cur.execute("DELETE FROM place_text_embeddings;")
        print("  🗑️ Cleared existing data")
        
        # Prepare data
        rows = []
        for emb in embeddings:
            rows.append((
                emb.place_id,
                emb.embedding.tolist(),  # Convert numpy to list
                emb.embedding_type,  # Maps to content_type
                emb.source_text[:2000] if emb.source_text else None,
                json.dumps(emb.metadata)
            ))
        
        # Batch insert
        for i in tqdm(range(0, len(rows), batch_size), desc="Uploading text"):
            batch = rows[i:i + batch_size]
            execute_values(cur, """
                INSERT INTO place_text_embeddings (place_id, embedding, content_type, source_text, metadata)
                VALUES %s
            """, batch)
        
        conn.commit()
    
    print(f"✅ Uploaded {len(embeddings)} text embeddings")


def upload_image_embeddings(conn, batch_size=50):
    """Upload image embeddings"""
    pkl_file = RAG_PROCESSED_DIR / "image_embeddings.pkl"
    
    with open(pkl_file, 'rb') as f:
        embeddings = pickle.load(f)
    
    print(f"\n🖼️ Uploading {len(embeddings)} image embeddings...")
    
    with conn.cursor() as cur:
        # Clear existing
        cur.execute("DELETE FROM place_image_embeddings;")
        print("  🗑️ Cleared existing data")
        
        # Prepare data
        rows = []
        for emb in embeddings:
            # Include scene_type in metadata
            meta = emb.metadata.copy() if emb.metadata else {}
            meta['scene_type'] = emb.scene_type
            rows.append((
                emb.place_id,
                emb.embedding.tolist(),
                emb.image_url,
                json.dumps(meta)
            ))
        
        # Batch insert
        for i in tqdm(range(0, len(rows), batch_size), desc="Uploading images"):
            batch = rows[i:i + batch_size]
            execute_values(cur, """
                INSERT INTO place_image_embeddings (place_id, embedding, image_url, metadata)
                VALUES %s
            """, batch)
        
        conn.commit()
    
    print(f"✅ Uploaded {len(embeddings)} image embeddings")


def upload_metadata(conn, batch_size=50):
    """Upload places metadata"""
    json_file = RAG_PROCESSED_DIR / "places_normalized.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        places = json.load(f)
    
    print(f"\n📋 Uploading metadata for {len(places)} places...")
    
    with conn.cursor() as cur:
        # Clear existing
        cur.execute("DELETE FROM places_metadata;")
        print("  🗑️ Cleared existing data")
        
        # Prepare data
        for i in tqdm(range(0, len(places), batch_size), desc="Uploading metadata"):
            batch = places[i:i + batch_size]
            
            for place in batch:
                coords = place.get('coordinates', {})
                lat = coords.get('latitude', 0)
                lng = coords.get('longitude', 0)
                
                raw_data = {
                    'phone': place.get('phone'),
                    'website': place.get('website'),
                    'google_maps_url': place.get('google_maps_url'),
                    'description': place.get('description'),
                    'specialty': place.get('specialty'),
                    'photos_count': place.get('photos_count'),
                    'reviews_count': place.get('reviews_count')
                }
                
                cur.execute("""
                    INSERT INTO places_metadata 
                    (place_id, name, name_vi, category, address, rating, price_min, price_max, tags, coordinates, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)
                    ON CONFLICT (place_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        category = EXCLUDED.category,
                        rating = EXCLUDED.rating,
                        updated_at = now()
                """, (
                    place.get('id'),
                    place.get('name'),
                    place.get('name_vi'),
                    place.get('category'),
                    place.get('address'),
                    place.get('rating'),
                    place.get('price_min'),
                    place.get('price_max'),
                    place.get('tags', []),
                    lng, lat,
                    json.dumps(raw_data)
                ))
        
        conn.commit()
    
    print(f"✅ Uploaded metadata for {len(places)} places")


def verify_upload(conn):
    """Verify upload counts"""
    print("\n📊 Verifying upload...")
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM place_text_embeddings;")
        text_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM place_image_embeddings;")
        image_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM places_metadata;")
        meta_count = cur.fetchone()[0]
        
        print(f"\n✅ VERIFICATION COMPLETE:")
        print(f"  📝 Text embeddings: {text_count}")
        print(f"  🖼️ Image embeddings: {image_count}")
        print(f"  📋 Places metadata: {meta_count}")
        
        return text_count, image_count, meta_count


def main():
    """Main upload function"""
    print("="*60)
    print("🚀 SUPABASE UPLOAD")
    print("="*60)
    
    conn = get_connection()
    print("✅ Connected to Supabase PostgreSQL")
    
    try:
        setup_schema(conn)
        upload_metadata(conn)
        upload_text_embeddings(conn)
        upload_image_embeddings(conn)
        verify_upload(conn)
        
        print("\n" + "="*60)
        print("🎉 ALL UPLOADS COMPLETE!")
        print("="*60)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
