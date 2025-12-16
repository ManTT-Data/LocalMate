-- RAG Vector Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- ============================================================================
-- 1. ENABLE EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- 2. TEXT EMBEDDINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS place_text_embeddings (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  place_id text NOT NULL,
  embedding_type text NOT NULL DEFAULT 'master',
  embedding vector(768) NOT NULL,  -- Gemini text-embedding-004 dimension
  source_text text,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Indexes for text embeddings
CREATE INDEX IF NOT EXISTS idx_text_place_id ON place_text_embeddings(place_id);
CREATE INDEX IF NOT EXISTS idx_text_emb_type ON place_text_embeddings(embedding_type);
CREATE INDEX IF NOT EXISTS idx_text_place_type ON place_text_embeddings(place_id, embedding_type);

-- Vector index (IVFFlat for approximate nearest neighbor search)
CREATE INDEX IF NOT EXISTS idx_text_embedding_vector 
  ON place_text_embeddings 
  USING ivfflat (embedding vector_cosine_ops) 
  WITH (lists = 100);

-- ============================================================================
-- 3. IMAGE EMBEDDINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS place_image_embeddings (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  place_id text NOT NULL,
  image_url text NOT NULL,
  embedding vector(768) NOT NULL,  -- SigLIP ViT-B-16 dimension
  scene_type text DEFAULT 'other',
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Indexes for image embeddings
CREATE INDEX IF NOT EXISTS idx_image_place_id ON place_image_embeddings(place_id);
CREATE INDEX IF NOT EXISTS idx_image_scene_type ON place_image_embeddings(scene_type);
CREATE INDEX IF NOT EXISTS idx_image_url ON place_image_embeddings(image_url);

-- Vector index
CREATE INDEX IF NOT EXISTS idx_image_embedding_vector 
  ON place_image_embeddings 
  USING ivfflat (embedding vector_cosine_ops) 
  WITH (lists = 100);

-- ============================================================================
-- 4. PLACES METADATA TABLE (for filtering)
-- ============================================================================
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

-- Indexes for metadata
CREATE INDEX IF NOT EXISTS idx_meta_category ON places_metadata(category);
CREATE INDEX IF NOT EXISTS idx_meta_rating ON places_metadata(rating);
CREATE INDEX IF NOT EXISTS idx_meta_tags ON places_metadata USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_meta_location ON places_metadata USING GIST(coordinates);

-- ============================================================================
-- 5. VECTOR SEARCH FUNCTIONS
-- ============================================================================

-- Text search function
CREATE OR REPLACE FUNCTION match_text_embeddings(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10,
  filter_embedding_type text DEFAULT NULL
)
RETURNS TABLE (
  place_id text,
  embedding_type text,
  similarity float,
  source_text text,
  metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.place_id,
    e.embedding_type,
    1 - (e.embedding <=> query_embedding) as similarity,
    e.source_text,
    e.metadata
  FROM place_text_embeddings e
  WHERE 
    (filter_embedding_type IS NULL OR e.embedding_type = filter_embedding_type)
    AND 1 - (e.embedding <=> query_embedding) > match_threshold
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Image search function
CREATE OR REPLACE FUNCTION match_image_embeddings(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 20,
  filter_scene_type text DEFAULT NULL
)
RETURNS TABLE (
  place_id text,
  image_url text,
  scene_type text,
  similarity float,
  metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.place_id,
    e.image_url,
    e.scene_type,
    1 - (e.embedding <=> query_embedding) as similarity,
    e.metadata
  FROM place_image_embeddings e
  WHERE 
    (filter_scene_type IS NULL OR e.scene_type = filter_scene_type)
    AND 1 - (e.embedding <=> query_embedding) > match_threshold
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Hybrid search with metadata filter
CREATE OR REPLACE FUNCTION match_places_hybrid(
  query_embedding vector(768),
  embedding_types text[] DEFAULT ARRAY['master'],
  category_filter text DEFAULT NULL,
  price_max_filter numeric DEFAULT NULL,
  rating_min_filter numeric DEFAULT NULL,
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  place_id text,
  name text,
  category text,
  rating numeric,
  similarity float,
  embedding_type text,
  source_text text
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.place_id,
    m.name,
    m.category,
    m.rating,
    1 - (e.embedding <=> query_embedding) as similarity,
    e.embedding_type,
    e.source_text
  FROM place_text_embeddings e
  JOIN places_metadata m ON e.place_id = m.place_id
  WHERE 
    e.embedding_type = ANY(embedding_types)
    AND 1 - (e.embedding <=> query_embedding) > match_threshold
    AND (category_filter IS NULL OR m.category ILIKE '%' || category_filter || '%')
    AND (price_max_filter IS NULL OR m.price_max <= price_max_filter)
    AND (rating_min_filter IS NULL OR m.rating >= rating_min_filter)
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Find nearby places
CREATE OR REPLACE FUNCTION find_nearby_places(
  lat float,
  lng float,
  radius_km float DEFAULT 2.0,
  limit_count int DEFAULT 10
)
RETURNS TABLE (
  place_id text,
  name text,
  category text,
  rating numeric,
  distance_km float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    m.place_id,
    m.name,
    m.category,
    m.rating,
    ST_Distance(m.coordinates, ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography) / 1000 as distance_km
  FROM places_metadata m
  WHERE ST_DWithin(
    m.coordinates, 
    ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography, 
    radius_km * 1000
  )
  ORDER BY distance_km
  LIMIT limit_count;
END;
$$;

-- ============================================================================
-- 6. GRANT PERMISSIONS
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON place_text_embeddings TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON place_image_embeddings TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON places_metadata TO anon, authenticated;
GRANT EXECUTE ON FUNCTION match_text_embeddings TO anon, authenticated;
GRANT EXECUTE ON FUNCTION match_image_embeddings TO anon, authenticated;
GRANT EXECUTE ON FUNCTION match_places_hybrid TO anon, authenticated;
GRANT EXECUTE ON FUNCTION find_nearby_places TO anon, authenticated;
