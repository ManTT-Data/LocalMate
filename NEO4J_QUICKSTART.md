# 🚀 Neo4j AuraDB Import - Quick Start Guide

## Prerequisites

✅ Python 3.7+
✅ Neo4j AuraDB Free account
✅ Crawled data (300 places)

## Step 1: Create AuraDB Instance (5 minutes)

1. Go to https://neo4j.com/cloud/aura/
2. Sign up / Login with Google/Email
3. Click "Create Database" → Select "Free"
4. Database details:
   - Name: `danang-tourism`
   - Region: Choose closest to Vietnam (Singapore/Tokyo)
5. **IMPORTANT**: Save credentials shown!
   ```
   Connection URI: neo4j+s://xxxxx.databases.neo4j.io
   Username: neo4j
   Password: (auto-generated, save this!)
   ```

## Step 2: Prepare Data

```bash
# Merge Excel data with crawled data (if not done)
python3 merge_data.py

# Verify output
ls data/places/  # Should see ~300 folders
```

## Step 3: Import to Neo4j

```bash
# Install driver
pip install neo4j

# Run import
python3 import_to_neo4j.py \
  --uri "neo4j+s://YOUR-INSTANCE-ID.databases.neo4j.io" \
  --user "neo4j" \
  --password "YOUR-PASSWORD" \
  --clear

# Without spatial relationships (faster, ~5min)
python3 import_to_neo4j.py \
  --uri "..." \
  --password "..." \
  --skip-spatial
```

**Import time**:
- Without spatial: ~5 minutes
- With spatial (recommended): ~15 minutes

## Step 4: Verify Import

1. Go to https://console.neo4j.io
2. Login
3. Open "danang-tourism" database
4. Click "Query" or "Explore"

### Quick Test Queries

#### 1. Count nodes
```cypher
MATCH (n)
RETURN labels(n) as type, count(n) as count
ORDER BY count DESC
```

Expected:
```
Photo: ~7,798
Review: ~2,820
Place: ~300
Category: ~10
```

#### 2. Top-rated places with photos
```cypher
MATCH (p:Place)
WHERE p.photos_count >= 20 AND p.rating >= 4.5
RETURN p.name, p.rating, p.category, p.photos_count
ORDER BY p.rating DESC
LIMIT 10
```

#### 3. Find places near coordinates
```cypher
MATCH (p:Place)
WHERE p.latitude IS NOT NULL
WITH p, 
  point.distance(
    point({latitude: 16.0486, longitude: 108.2478}),
    point({latitude: p.latitude, longitude: p.longitude})
  ) / 1000.0 as distance_km
WHERE distance_km < 2
RETURN p.name, p.category, round(distance_km, 2) as km
ORDER BY distance_km
LIMIT 10
```

#### 4. Explore nearby places
```cypher
MATCH (p1:Place)-[n:NEAR]-(p2:Place)
WHERE p1.rating >= 4.5 AND p2.rating >= 4.5
  AND n.distance_km < 1
RETURN p1.name, p2.name, n.distance_km
ORDER BY n.distance_km
LIMIT 20
```

#### 5. Category breakdown
```cypher
MATCH (c:Category)<-[:IN_CATEGORY]-(p:Place)
RETURN c.name as category,
       count(p) as places,
       round(avg(p.rating), 2) as avg_rating
ORDER BY places DESC
```

## Step 5: Share with Team

**Share these credentials**:
```
URL: https://console.neo4j.io
Database: danang-tourism
Username: neo4j
Password: (the one you saved)
```

**What teammates can do**:
- ✅ Browse graph visually
- ✅ Run Cypher queries
- ✅ Export data
- ✅ Analyze patterns

## Python API Access (for backend)

```python
from neo4j import GraphDatabase

# Connect
driver = GraphDatabase.driver(
    "neo4j+s://YOUR-ID.databases.neo4j.io",
    auth=("neo4j", "your-password")
)

# Query example
with driver.session() as session:
    result = session.run("""
        MATCH (p:Place)
        WHERE p.rating >= 4.5
        RETURN p.name, p.rating, p.category
        LIMIT 10
    """)
    
    for record in result:
        print(f"{record['p.name']}: {record['p.rating']} ⭐")

driver.close()
```

## Troubleshooting

### Connection timeout
- Check URI format: must be `neo4j+s://` (with `s`)
- Verify password (no typos)

### Import fails
- Run `python3 merge_data.py` first
- Check `data/places/` folder exists

### No spatial relationships
- Add `--skip-spatial` to import faster
- Can add later with separate script

## Advanced Queries

### Places with most photos
```cypher
MATCH (p:Place)
RETURN p.name, p.photos_count, p.category
ORDER BY p.photos_count DESC
LIMIT 20
```

### High-rated clusters
```cypher
MATCH (p1:Place)-[:NEAR*1..2]-(p2:Place)
WHERE p1.rating >= 4.5 AND p2.rating >= 4.5
WITH p1, collect(DISTINCT p2) as nearby
WHERE size(nearby) >= 3
RETURN p1.name, p1.rating, size(nearby) as nearby_count
ORDER BY nearby_count DESC
LIMIT 10
```

### Reviews sentiment (manual analysis)
```cypher
MATCH (p:Place)-[:HAS_REVIEW]->(r:Review)
WHERE r.rating >= 4
RETURN p.name, collect(r.text)[0..3] as sample_reviews
LIMIT 5
```

## Next Steps

1. ✅ Import completed
2. ⚡ Integrate with Aura Engine backend
3. 📊 Add more relationships (e.g., SIMILAR_TO)
4. 🔍 Enable full-text search
5. 🤖 Add AI-powered recommendations

Enjoy your graph database! 🎉
