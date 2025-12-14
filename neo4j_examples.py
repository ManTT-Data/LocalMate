"""
Neo4j Query Examples - Danang Tourism Database
Use these queries in Neo4j Browser or Python
"""

from neo4j import GraphDatabase

# Connection setup
URI = "neo4j+s://64ff7b02.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Example 1: Get all places with high ratings
def get_top_rated_places(limit=10):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WHERE p.rating >= 4.5
            RETURN p.name, p.rating, p.category, p.photos_count
            ORDER BY p.rating DESC, p.photos_count DESC
            LIMIT $limit
        """, limit=limit)
        
        for record in result:
            print(f"{record['p.name']}: {record['p.rating']}⭐ - {record['p.category']}")

# Example 2: Find places near coordinates
def find_nearby_places(lat, lng, radius_km=2):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WHERE p.latitude IS NOT NULL
            WITH p, point.distance(
                point({latitude: $lat, longitude: $lng}),
                point({latitude: p.latitude, longitude: p.longitude})
            ) / 1000.0 as distance_km
            WHERE distance_km <= $radius
            RETURN p.name, p.category, p.rating, distance_km
            ORDER BY distance_km
        """, lat=lat, lng=lng, radius=radius_km)
        
        for record in result:
            print(f"{record['p.name']}: {record['distance_km']:.2f}km - {record['p.rating']}⭐")

# Example 3: Get place details with photos and reviews
def get_place_details(place_name):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place {name: $name})
            OPTIONAL MATCH (p)-[:HAS_PHOTO]->(photo:Photo)
            OPTIONAL MATCH (p)-[:HAS_REVIEW]->(review:Review)
            RETURN p, 
                   count(DISTINCT photo) as photo_count,
                   count(DISTINCT review) as review_count,
                   collect(DISTINCT review.text)[0..3] as sample_reviews
        """, name=place_name)
        
        record = result.single()
        if record:
            place = record['p']
            print(f"Name: {place['name']}")
            print(f"Rating: {place['rating']}")
            print(f"Address: {place['address']}")
            print(f"Photos: {record['photo_count']}")
            print(f"Reviews: {record['review_count']}")

# Example 4: Find restaurant clusters (places near each other)
def find_restaurant_clusters():
    with driver.session() as session:
        result = session.run("""
            MATCH (p1:Place)-[n:NEAR]-(p2:Place)
            WHERE p1.category CONTAINS 'restaurant' 
              AND p2.category CONTAINS 'restaurant'
              AND n.distance_km < 0.5
            RETURN p1.name, p2.name, n.distance_km
            ORDER BY n.distance_km
            LIMIT 20
        """)
        
        for record in result:
            print(f"{record['p1.name']} ↔ {record['p2.name']}: {record['n.distance_km']}km")

# Example 5: Category statistics
def get_category_stats():
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Category)<-[:IN_CATEGORY]-(p:Place)
            RETURN c.name as category,
                   count(p) as places,
                   avg(p.rating) as avg_rating,
                   sum(p.photos_count) as total_photos
            ORDER BY places DESC
        """)
        
        print("\nCategory Statistics:")
        for record in result:
            print(f"{record['category']}: {record['places']} places, "
                  f"avg {record['avg_rating']:.1f}⭐, "
                  f"{record['total_photos']} photos")

if __name__ == '__main__':
    print("=== Top Rated Places ===")
    get_top_rated_places(5)
    
    print("\n=== Category Statistics ===")
    get_category_stats()
    
    print("\n=== Places Near My An Beach ===")
    find_nearby_places(16.048, 108.247, radius_km=1)
    
    driver.close()
