# Database Setup Guide

Hướng dẫn setup Supabase database cho LocalMate Da Nang.

---

## 1. Supabase Project Setup

### 1.1. Tạo Supabase Project

1. Đăng nhập [Supabase Dashboard](https://app.supabase.com)
2. Click **New Project**
3. Điền thông tin:
   - Name: `localmate-danang`
   - Database Password: (lưu lại password này)
   - Region: Singapore (gần Việt Nam)
4. Click **Create new project**

### 1.2. Lấy Connection Info

Vào **Settings > Database**, copy các thông tin sau vào `.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

---

## 2. Enable Extensions

Chạy trong **SQL Editor**:

```sql
-- Enable pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable trigram for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 3. Create Tables

Chạy lần lượt các SQL sau:

### 3.1. Profiles Table

```sql
-- Profiles table (linked to auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL DEFAULT '',
    phone TEXT,
    role TEXT NOT NULL DEFAULT 'tourist' CHECK (role IN ('tourist', 'driver', 'admin')),
    locale TEXT NOT NULL DEFAULT 'vi_VN',
    avatar_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);
```

### 3.2. Auto-create Profile on Signup

```sql
-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        'tourist'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 3.3. Itineraries Table

```sql
CREATE TABLE IF NOT EXISTS public.itineraries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    total_days INTEGER NOT NULL CHECK (total_days >= 1),
    total_budget NUMERIC(12, 2),
    currency TEXT NOT NULL DEFAULT 'VND',
    meta JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON itineraries(user_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_created_at ON itineraries(created_at);

-- Enable RLS
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can CRUD own itineraries" ON itineraries
    FOR ALL USING (auth.uid() = user_id);
```

### 3.4. Itinerary Stops Table

```sql
CREATE TABLE IF NOT EXISTS public.itinerary_stops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    itinerary_id UUID NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
    day_index INTEGER NOT NULL CHECK (day_index >= 1),
    order_index INTEGER NOT NULL CHECK (order_index >= 1),
    place_id TEXT NOT NULL,
    arrival_time TIMESTAMPTZ,
    stay_minutes INTEGER,
    notes TEXT,
    tags TEXT[],
    snapshot JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_stops_itinerary_id ON itinerary_stops(itinerary_id);
CREATE INDEX IF NOT EXISTS idx_stops_place_id ON itinerary_stops(place_id);
CREATE INDEX IF NOT EXISTS idx_stops_day_order ON itinerary_stops(itinerary_id, day_index, order_index);

-- Enable RLS
ALTER TABLE itinerary_stops ENABLE ROW LEVEL SECURITY;

-- RLS Policy (through itinerary ownership)
CREATE POLICY "Users can CRUD own stops" ON itinerary_stops
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM itineraries 
            WHERE itineraries.id = itinerary_stops.itinerary_id 
            AND itineraries.user_id = auth.uid()
        )
    );
```

### 3.5. Place Embeddings Table (pgvector)

```sql
CREATE TABLE IF NOT EXISTS public.place_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id TEXT NOT NULL UNIQUE,
    text_embedding VECTOR(768),  -- text-embedding-004
    image_embedding VECTOR(512), -- CLIP
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Vector indexes (HNSW for fast similarity search)
CREATE INDEX IF NOT EXISTS idx_place_text_embedding 
    ON place_embeddings USING hnsw (text_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_place_image_embedding 
    ON place_embeddings USING hnsw (image_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_place_embeddings_place_id 
    ON place_embeddings(place_id);
```

### 3.6. Semantic Search Function

```sql
-- Function for semantic text search
CREATE OR REPLACE FUNCTION search_places_by_text(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    place_id TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pe.place_id,
        (1 - (pe.text_embedding <=> query_embedding))::FLOAT as similarity,
        pe.metadata
    FROM place_embeddings pe
    WHERE 1 - (pe.text_embedding <=> query_embedding) > match_threshold
    ORDER BY pe.text_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

---

## 4. Bookings Table (Optional)

```sql
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    itinerary_id UUID REFERENCES itineraries(id) ON DELETE SET NULL,
    stop_id UUID REFERENCES itinerary_stops(id) ON DELETE SET NULL,
    provider TEXT NOT NULL,
    type TEXT NOT NULL,
    external_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    price NUMERIC(12, 2),
    currency TEXT NOT NULL DEFAULT 'VND',
    place_id TEXT,
    raw_request JSONB,
    raw_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_itinerary_id ON bookings(itinerary_id);

ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own bookings" ON bookings
    FOR ALL USING (auth.uid() = user_id);
```

---

## 5. Verify Setup

```sql
-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check extensions
SELECT * FROM pg_extension;

-- Test profile creation (after creating a user)
SELECT * FROM profiles LIMIT 5;
```

---

## 6. Common Issues

### Issue: "Permission denied"
**Solution:** Đảm bảo dùng SQL Editor trong Supabase (có quyền superuser).

### Issue: "Extension not found"
**Solution:** pgvector có sẵn trong Supabase, chỉ cần `CREATE EXTENSION`.

### Issue: RLS blocking queries
**Solution:** Trong development, có thể tạm disable RLS:
```sql
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
```

---

## 7. Neo4j Aura Setup

Neo4j lưu trữ **Place data** và các **relationship không gian** (nearby, similar, etc.).

### 7.1. Tạo Neo4j Aura Instance

1. Đăng ký tại [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Click **New Instance** → Chọn **AuraDB Free** (hoặc Professional)
3. Chọn **Region**: Singapore hoặc gần Việt Nam
4. Lưu lại credentials:
   - **Connection URI**: `neo4j+s://xxxxx.databases.neo4j.io`
   - **Username**: `neo4j`
   - **Password**: (auto-generated)

### 7.2. Cập nhật `.env`

```env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 7.3. Tạo Schema (Constraints & Indexes)

Chạy trong **Neo4j Browser** hoặc **Aura Console**:

```cypher
// Constraint: Place ID phải unique
CREATE CONSTRAINT place_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.id IS UNIQUE;

// Index cho tìm kiếm theo category
CREATE INDEX place_category IF NOT EXISTS
FOR (p:Place) ON (p.category);

// Index cho spatial queries
CREATE POINT INDEX place_location IF NOT EXISTS
FOR (p:Place) ON (p.location);

// Index cho rating
CREATE INDEX place_rating IF NOT EXISTS
FOR (p:Place) ON (p.rating);
```

### 7.4. Place Node Schema (Reference)

Structure dữ liệu của một `Place` node (không chạy code này):

```cypher
/*
(:Place {
    id: "place_001",              // Unique identifier
    name: "Bà Nà Hills",
    name_en: "Ba Na Hills",
    category: "attraction",       // attraction, restaurant, cafe, beach, hotel
    subcategory: "theme_park",
    lat: 15.9977,
    lng: 107.9875,
    location: point({latitude: 15.9977, longitude: 107.9875}),
    rating: 4.5,
    review_count: 1250,
    price_level: 3,               // 1-4
    description: "Khu du lịch nổi tiếng với cầu Vàng...",
    description_en: "Famous resort with Golden Bridge...",
    address: "Hòa Vang, Đà Nẵng",
    opening_hours: "07:00-22:00",
    tags: ["family", "instagram", "nature"],
    image_url: "https://...",
    google_place_id: "ChIJ..."
})
*/
```

### 7.5. Relationships (Reference)

Các loại quan hệ giữa các Places (không chạy code này, xem ví dụ cụ thể ở 7.6):

```cypher
/*
// NEAR_TO: Places gần nhau
CREATE (p1:Place)-[:NEAR_TO {distance_km: 2.5}]->(p2:Place)

// SIMILAR_TO: Places tương tự (cùng category, interests)
CREATE (p1:Place)-[:SIMILAR_TO {score: 0.85}]->(p2:Place)

// RECOMMENDED_AFTER: Gợi ý đi tiếp
CREATE (p1:Place)-[:RECOMMENDED_AFTER {reason: "lunch nearby"}]->(p2:Place)
*/
```

### 7.6. Sample Data (Đà Nẵng Highlights)

Chạy từng block code sau đây riêng biệt (nếu copy paste vào Aura Console thì chạy từng phần):

#### Bước 1: Tạo Places

```cypher
CREATE (:Place {
    id: "danang_dragon_bridge",
    name: "Cầu Rồng",
    name_en: "Dragon Bridge",
    category: "attraction",
    subcategory: "landmark",
    lat: 16.0611,
    lng: 108.2272,
    location: point({latitude: 16.0611, longitude: 108.2272}),
    rating: 4.6,
    review_count: 5200,
    price_level: 1,
    description: "Cầu rồng phun lửa và nước vào cuối tuần",
    tags: ["free", "night", "instagram", "family"]
});

CREATE (:Place {
    id: "danang_my_khe_beach",
    name: "Bãi biển Mỹ Khê",
    name_en: "My Khe Beach",
    category: "beach",
    lat: 16.0544,
    lng: 108.2452,
    location: point({latitude: 16.0544, longitude: 108.2452}),
    rating: 4.7,
    review_count: 8500,
    price_level: 1,
    description: "Một trong những bãi biển đẹp nhất châu Á",
    tags: ["beach", "sunrise", "free", "instagram"]
});

CREATE (:Place {
    id: "danang_bana_hills",
    name: "Bà Nà Hills",
    name_en: "Ba Na Hills",
    category: "attraction",
    subcategory: "theme_park",
    lat: 15.9977,
    lng: 107.9875,
    location: point({latitude: 15.9977, longitude: 107.9875}),
    rating: 4.5,
    review_count: 12500,
    price_level: 3,
    description: "Khu du lịch với Cầu Vàng nổi tiếng",
    tags: ["family", "instagram", "nature", "cable_car"]
});
```

#### Bước 2: Tạo Relationships

Sau khi tạo xong Places ở trên, chạy tiếp lệnh này:

```cypher
MATCH (p1:Place {id: "danang_dragon_bridge"})
MATCH (p2:Place {id: "danang_my_khe_beach"})
MERGE (p1)-[:NEAR_TO {distance_km: 1.8}]->(p2)
MERGE (p2)-[:NEAR_TO {distance_km: 1.8}]->(p1);
```

### 7.7. Verify Neo4j Setup

```cypher
// Check node count
MATCH (p:Place) RETURN count(p) as place_count;

// Check constraints
SHOW CONSTRAINTS;

// Check indexes
SHOW INDEXES;

// Test spatial query
MATCH (p:Place)
WITH p, point.distance(
    p.location,
    point({latitude: 16.06, longitude: 108.22})
) / 1000 as distance_km
WHERE distance_km <= 5
RETURN p.name, distance_km
ORDER BY distance_km;
```

---

## 8. Common Neo4j Issues

### Issue: "Unable to connect"
**Solution:** Kiểm tra `NEO4J_URI` phải có prefix `neo4j+s://` (với SSL).

### Issue: "AuthenticationError"
**Solution:** Kiểm tra username/password trong `.env`, đảm bảo không có spaces thừa.

### Issue: "Point index not found"
**Solution:** Neo4j Aura Free có thể không hỗ trợ point index. Dùng lat/lng thay vì `point()`.
