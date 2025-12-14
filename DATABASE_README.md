# 🗺️ Danang Tourism Graph Database

Neo4j database chứa **301 địa điểm du lịch Đà Nẵng** với photos, reviews, và spatial relationships.

## 📊 Database Overview

### Statistics
- **Places**: 302 địa điểm (hotels, restaurants, cafes, fitness...)
- **Photos**: 7,858 ảnh (trung bình 26 ảnh/địa điểm)
- **Reviews**: 671 đánh giá
- **Categories**: 69 categories
- **Spatial Links**: 21,936 NEAR relationships (< 2km)

### Data Sources
- **Crawled**: Google Maps (ratings, coordinates, photos, reviews)
- **Manual**: Excel sheets (descriptions, prices, specialties, opening hours)
- **Merged**: All places have complete data from both sources

---

## 🔌 Connection Info

```python
URI: neo4j+s://64ff7b02.databases.neo4j.io
Username: neo4j
Password: O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4
Database: neo4j
```

**Web Access**: https://console.neo4j.io

### Data Quality
- ✅ **100%** have coordinates (perfect for spatial queries)
- ✅ **99%** have ratings
- ✅ **90%** have phone numbers
- ✅ **85%** have Excel metadata (price, description)
- ✅ **85%** have 30 photos (perfect crawl)

---

## 🏗️ Graph Schema

### Node Types
                                                                                                                                                  
#### Place
```cypher
(:Place {
  id: string,              # unique slug
  name: string,            # "Hyatt Regency Danang"
  name_vi: string,         # Vietnamese name from Excel
  rating: float,           # 0.0 - 5.0
  category: string,        # "Hotel", "Restaurant"...
  
  // Location
  latitude: float,
  longitude: float,
  address: string,
  
  // Metadata
  price_range: string,     # from Excel
  description: string,     # from Excel
  specialty: string,       # from Excel
  
  // Contact
  phone: string,
  website: string,
  google_maps_url: string,
  
  // Stats
  photos_count: int,
  reviews_count: int
  
  // NOTE: price_range, description, specialty are from Excel
  // and are available for ~85% of places
})
```

#### Photo
```cypher
(:Photo {
  id: string,
  filename: string,
  path: string,            # "place_slug/photos/photo_001.jpg"
  order: int
})
```

#### Review
```cypher
(:Review {
  id: string,
  reviewer: string,
  rating: int,
  text: string
})
```

#### Category
```cypher
(:Category {
  name: string            # "Restaurant", "Hotel"...
})
```

### Relationships

```cypher
(:Place)-[:IN_CATEGORY]->(:Category)
(:Place)-[:HAS_PHOTO]->(:Photo)
(:Place)-[:HAS_REVIEW]->(:Review)
(:Place)-[:NEAR {distance_km: float}]->(:Place)
```

---

## 🔍 Common Queries

### 1. Get Top-Rated Places
```cypher
MATCH (p:Place)
WHERE p.rating >= 4.5
RETURN p.name, p.rating, p.category, p.photos_count
ORDER BY p.rating DESC, p.photos_count DESC
LIMIT 10
```

### 2. Find Places Near Location
```cypher
// Find restaurants within 2km of My An Beach
MATCH (p:Place)
WHERE p.category CONTAINS 'restaurant'
WITH p, point.distance(
  point({latitude: 16.0486, longitude: 108.2478}),
  point({latitude: p.latitude, longitude: p.longitude})
) / 1000.0 as distance_km
WHERE distance_km <= 2
RETURN p.name, p.rating, p.address, distance_km
ORDER BY distance_km
```

### 3. Get Place with Photos & Reviews
```cypher
MATCH (p:Place {name: "Hyatt Regency Danang Resort and Spa"})
OPTIONAL MATCH (p)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (p)-[:HAS_REVIEW]->(review:Review)
RETURN p,
       count(DISTINCT photo) as photo_count,
       collect(DISTINCT photo.filename)[0..5] as sample_photos,
       count(DISTINCT review) as review_count,
       collect(DISTINCT review.text)[0..3] as sample_reviews
```

### 4. Find Nearby Places (Graph Traversal)
```cypher
// Find what's near InterContinental
MATCH (p:Place {name: "InterContinental Danang Sun Peninsula Resort"})-[n:NEAR]-(nearby:Place)
WHERE n.distance_km < 1
RETURN nearby.name, nearby.category, n.distance_km
ORDER BY n.distance_km
LIMIT 10
```

### 5. Category Statistics
```cypher
MATCH (c:Category)<-[:IN_CATEGORY]-(p:Place)
RETURN c.name as category,
       count(p) as places,
       avg(p.rating) as avg_rating,
       sum(p.photos_count) as total_photos
ORDER BY places DESC
```

### 6. Restaurant Clusters
```cypher
// Find restaurant-dense areas
MATCH (p1:Place)-[n:NEAR]-(p2:Place)
WHERE p1.category CONTAINS 'restaurant' 
  AND p2.category CONTAINS 'restaurant'
  AND n.distance_km < 0.5
WITH p1, count(p2) as nearby_count
WHERE nearby_count >= 3
RETURN p1.name, p1.address, nearby_count
ORDER BY nearby_count DESC
LIMIT 10
```

### 7. Search by Name (Case-Insensitive)
```cypher
MATCH (p:Place)
WHERE toLower(p.name) CONTAINS toLower("coffee")
RETURN p.name, p.category, p.rating
ORDER BY p.rating DESC
LIMIT 10
```

### 8. Full-Text Search (if enabled)
```cypher
// Search in descriptions and specialties
MATCH (p:Place)
WHERE p.description CONTAINS "beach" 
   OR p.specialty CONTAINS "seafood"
RETURN p.name, p.description, p.specialty
LIMIT 10
```

---

## 🐍 Python Usage

### Setup
```bash
pip install neo4j
```

### Basic Connection
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j+s://64ff7b02.databases.neo4j.io",
    auth=("neo4j", "O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4")
)

# Always close when done
driver.close()
```

### Query Examples
See `neo4j_examples.py` and `neo4j_use_cases.py` for detailed examples.

---

## 🎯 Use Cases

### Tourism Recommendation Engine
- Find places near user location
- Filter by category, rating, price
- Use NEAR relationships for "nearby attractions"

### Data Analysis
- Category distribution
- Rating correlations
- Geographic clustering

### Graph-RAG Integration
- Retrieve relevant places based on user query
- Use relationships for context expansion
- Combine with LLM for natural language responses

---

## 📁 Related Files

- `neo4j_examples.py` - Basic query examples
- `neo4j_use_cases.py` - Real-world use cases
- `NEO4J_QUICKSTART.md` - Setup guide
- `import_to_neo4j.py` - Import script (if need to re-import)

---

## 🔒 Security Notes

- **Password** in this doc is for development only
- For production: Use environment variables
- Rotate password regularly via Neo4j Console
- Enable IP whitelist if needed

---

## 💡 Tips

1. **Use indexes**: Already created on `Place.id`, `Place.name`, `Place.category`
2. **Spatial queries**: Use `point.distance()` for geographic searches
3. **Limit results**: Always use `LIMIT` to avoid overwhelming queries
4. **Relationships**: Leverage NEAR for proximity-based recommendations

---

## 📞 Support

Questions? Check:
- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/
- Neo4j Python Driver: https://neo4j.com/docs/python-manual/
- AuraDB Console: https://console.neo4j.io

---

**Last Updated**: 2025-12-07  
**Database Version**: Neo4j 5.x (AuraDB Free)
