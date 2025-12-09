# Database Schema

## 1. Overview

**Hybrid Database Architecture:**

| Database | Purpose |
|----------|---------|
| **Supabase PostgreSQL** | Structured data, users, bookings, itineraries, vector embeddings |
| **Neo4j Aura** | Graph data - Places và relationships không gian |

**Chính:**

* `profiles` – thông tin profile cơ bản (liên kết với `auth.users` của Supabase).
* `driver_profiles` – thông tin bổ sung cho tài xế.
* `itineraries` – itinerary tổng quát (trip của user).
* `itinerary_stops` – từng điểm dừng trong itinerary (trỏ sang Neo4j `place_id`).
* `bookings` – booking thực hiện qua MCP (Grab, hotel, ticket…).
* `affiliate_programs` – thông tin venues/đối tác có hoa hồng.
* `place_embeddings` – vector embeddings cho semantic search (pgvector).

**Quan hệ (logical ER):**

```
auth.users (Supabase managed)
    │
    └── 1:1 ── profiles
                  │
                  ├── 1:N ── itineraries
                  │              │
                  │              └── 1:N ── itinerary_stops
                  │
                  ├── 1:N ── bookings
                  │
                  └── 1:1 ── driver_profiles (if role=driver)
```

---

## 2. Tables Detail

### 2.1. `profiles`

> [!NOTE]
> Thay thế table `users` cũ. Auth được xử lý bởi Supabase Auth (`auth.users`).
> Table này chỉ lưu thông tin profile bổ sung.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, FK → auth.users(id) | Profile ID = Auth User ID |
| full_name | TEXT | NOT NULL | Tên hiển thị |
| phone | TEXT | NULL | Số điện thoại |
| role | TEXT | NOT NULL, CHECK in ('tourist','driver','admin') | Phân quyền |
| locale | TEXT | NOT NULL, default `'vi_VN'` | Ngôn ngữ ưu tiên |
| avatar_url | TEXT | NULL | URL avatar |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | Thời gian tạo |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | Lần cập nhật gần nhất |

**Indexes:**

* `idx_profiles_role` (role)

**RLS Policy:**
```sql
-- Users can only read/update their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);
```

---

### 2.2. `driver_profiles`

Thông tin chi tiết cho driver, map 1–1 với `profiles`.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default `gen_random_uuid()` | Driver profile ID |
| user_id | UUID | UNIQUE, NOT NULL, FK → profiles(id) | Liên kết tới `profiles` |
| grab_driver_id | TEXT | NULL | ID của tài xế bên Grab |
| languages | TEXT[] | NOT NULL, default `ARRAY['vi']` | Các ngôn ngữ driver có thể nói |
| rating | NUMERIC(2,1) | NULL | Rating trung bình |
| bio | TEXT | NULL | Mô tả ngắn |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes:**

* `idx_driver_profiles_user_id` UNIQUE(user_id)
* `idx_driver_profiles_grab_driver_id` (grab_driver_id)

---

### 2.3. `itineraries`

Một itinerary ứng với một chuyến đi / plan của user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default `gen_random_uuid()` | Itinerary ID |
| user_id | UUID | NOT NULL, FK → profiles(id) | Chủ sở hữu itinerary |
| title | TEXT | NOT NULL | Tên itinerary |
| start_date | DATE | NULL | Ngày bắt đầu |
| end_date | DATE | NULL | Ngày kết thúc |
| total_days | INT | NOT NULL, CHECK (total_days >= 1) | Số ngày |
| total_budget | NUMERIC(12,2) | NULL | Tổng budget dự kiến |
| currency | TEXT | NOT NULL, default `'VND'` | Loại tiền tệ |
| meta | JSONB | NULL | Extra info (family size, interests) |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes:**

* `idx_itineraries_user_id` (user_id)
* `idx_itineraries_created_at` (created_at)

**RLS Policy:**
```sql
CREATE POLICY "Users can CRUD own itineraries" ON itineraries
    FOR ALL USING (auth.uid() = user_id);
```

---

### 2.4. `itinerary_stops`

Từng điểm dừng trong itinerary, trỏ tới **Neo4j Place bằng `place_id`**.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default `gen_random_uuid()` | Stop ID |
| itinerary_id | UUID | NOT NULL, FK → itineraries(id) | Itinerary chứa stop |
| day_index | INT | NOT NULL, >= 1 | Ngày thứ mấy trong trip |
| order_index | INT | NOT NULL, >= 1 | Thứ tự trong ngày |
| place_id | TEXT | NOT NULL | **Neo4j `Place.id`** |
| arrival_time | TIMESTAMPTZ | NULL | Time dự kiến đến |
| stay_minutes | INT | NULL | Thời gian ở đó |
| notes | TEXT | NULL | Ghi chú riêng |
| tags | TEXT[] | NULL | Tags |
| snapshot | JSONB | NULL | Snapshot từ Neo4j |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes:**

* `idx_itinerary_stops_itinerary_id` (itinerary_id)
* `idx_itinerary_stops_place_id` (place_id)
* `idx_itinerary_stops_day_order` (itinerary_id, day_index, order_index)

---

### 2.5. `bookings`

Lưu các booking thực hiện qua MCP.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default `gen_random_uuid()` | Booking ID |
| user_id | UUID | NOT NULL, FK → profiles(id) | Ai tạo booking |
| itinerary_id | UUID | NULL, FK → itineraries(id) | Gắn với itinerary |
| stop_id | UUID | NULL, FK → itinerary_stops(id) | Gắn với stop |
| provider | TEXT | NOT NULL | 'grab', 'agoda', 'klook' |
| type | TEXT | NOT NULL | 'ride', 'hotel', 'ticket' |
| external_id | TEXT | NOT NULL | ID bên provider |
| status | TEXT | NOT NULL | 'pending','confirmed','cancelled' |
| price | NUMERIC(12,2) | NULL | Giá thực tế |
| currency | TEXT | NOT NULL, default 'VND' | Loại tiền |
| place_id | TEXT | NULL | Neo4j Place id |
| raw_request | JSONB | NULL | Payload request |
| raw_response | JSONB | NULL | Payload response |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes:**

* `idx_bookings_user_id` (user_id)
* `idx_bookings_itinerary_id` (itinerary_id)
* `idx_bookings_external` (provider, external_id)

---

### 2.6. `affiliate_programs`

Lưu các chương trình hoa hồng theo `place_id`.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default `gen_random_uuid()` | Affiliate ID |
| place_id | TEXT | NOT NULL | Neo4j Place id |
| partner_name | TEXT | NOT NULL | Tên partner |
| commission_rate | NUMERIC(5,2) | NOT NULL | % hoa hồng |
| tracking_url | TEXT | NOT NULL | URL tracking |
| active | BOOLEAN | NOT NULL, default TRUE | Đang active |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes:**

* `idx_affiliate_programs_place_id` (place_id)
* `idx_affiliate_programs_partner` (partner_name)

---

### 2.7. `place_embeddings`

> [!NOTE]
> Sử dụng **pgvector** extension của Supabase cho vector storage và similarity search.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default `gen_random_uuid()` | Embedding ID |
| place_id | TEXT | NOT NULL, UNIQUE | Neo4j Place id |
| text_embedding | VECTOR(768) | NULL | text-embedding-004 output |
| image_embedding | VECTOR(512) | NULL | CLIP output |
| metadata | JSONB | NULL | Place metadata cache |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` | |
| updated_at | TIMESTAMPTZ | NOT NULL, default `now()` | |

**Indexes:**

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create HNSW index for fast similarity search
CREATE INDEX idx_place_embeddings_text ON place_embeddings 
    USING hnsw (text_embedding vector_cosine_ops);

CREATE INDEX idx_place_embeddings_image ON place_embeddings 
    USING hnsw (image_embedding vector_cosine_ops);
```

**Functions:**

```sql
-- Semantic search function
CREATE OR REPLACE FUNCTION search_places_by_text(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    place_id TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pe.place_id,
        1 - (pe.text_embedding <=> query_embedding) as similarity
    FROM place_embeddings pe
    WHERE 1 - (pe.text_embedding <=> query_embedding) > match_threshold
    ORDER BY pe.text_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

---

## 3. Supabase Setup Commands

```sql
-- 1. Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. Create tables (run in order)
-- See individual table definitions above

-- 3. Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE itinerary_stops ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- 4. Create trigger for auto profile creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        'tourist'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```
