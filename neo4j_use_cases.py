"""
Real-World Use Cases for Danang Tourism Database
Practical examples for common scenarios
"""

from neo4j import GraphDatabase
import os

# Connection
URI = os.getenv("NEO4J_URI", "neo4j+s://64ff7b02.databases.neo4j.io")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


# USE CASE 1: Hotel Recommendation System
def recommend_hotels(budget=None, min_rating=4.0, near_beach=True):
    """
    Recommend hotels based on criteria
    
    Args:
        budget: 'low', 'medium', 'high' or None
        min_rating: minimum rating (0-5)
        near_beach: whether hotel should be near beach
    """
    with driver.session() as session:
        query = """
        MATCH (p:Place)
        WHERE p.category CONTAINS 'hotel' OR p.category CONTAINS 'resort'
          AND p.rating >= $min_rating
        """
        
        if near_beach:
            # My An Beach coordinates
            query += """
            WITH p, point.distance(
                point({latitude: 16.0486, longitude: 108.2478}),
                point({latitude: p.latitude, longitude: p.longitude})
            ) / 1000.0 as beach_distance
            WHERE beach_distance <= 3
            """
        else:
            query += "WITH p, null as beach_distance "
        
        query += """
        RETURN p.name, p.rating, p.price_range, p.address, 
               p.photos_count, beach_distance
        ORDER BY p.rating DESC, beach_distance ASC
        LIMIT 10
        """
        
        result = session.run(query, min_rating=min_rating)
        
        hotels = []
        for record in result:
            hotels.append({
                'name': record['p.name'],
                'rating': record['p.rating'],
                'price_range': record['p.price_range'],
                'beach_distance': record['beach_distance'],
                'photos': record['p.photos_count']
            })
        
        return hotels


# USE CASE 2: Restaurant Discovery Near User
def find_restaurants_nearby(lat, lng, cuisine=None, max_distance_km=1):
    """
    Find restaurants near user's current location
    
    Args:
        lat, lng: user's coordinates
        cuisine: filter by cuisine type (optional)
        max_distance_km: search radius
    """
    with driver.session() as session:
        query = """
        MATCH (p:Place)
        WHERE (p.category CONTAINS 'restaurant' OR p.category CONTAINS 'cafe')
        """
        
        if cuisine:
            query += " AND (toLower(p.category) CONTAINS toLower($cuisine) OR toLower(p.specialty) CONTAINS toLower($cuisine)) "
        
        query += """
        WITH p, point.distance(
            point({latitude: $lat, longitude: $lng}),
            point({latitude: p.latitude, longitude: p.longitude})
        ) / 1000.0 as distance_km
        WHERE distance_km <= $max_distance
        RETURN p.name, p.category, p.rating, p.specialty, 
               p.price_range, p.phone, distance_km
        ORDER BY distance_km, p.rating DESC
        """
        
        result = session.run(query, 
                           lat=lat, lng=lng, 
                           cuisine=cuisine,
                           max_distance=max_distance_km)
        
        return [dict(record) for record in result]


# USE CASE 3: Day Trip Planner
def plan_day_trip(start_lat, start_lng, interests=['restaurant', 'cafe', 'beach']):
    """
    Create a day trip itinerary based on proximity
    
    Args:
        start_lat, start_lng: starting point
        interests: list of place types interested in
    """
    with driver.session() as session:
        # Find starting point (nearest place)
        start_query = """
        MATCH (p:Place)
        WITH p, point.distance(
            point({latitude: $lat, longitude: $lng}),
            point({latitude: p.latitude, longitude: p.longitude})
        ) / 1000.0 as distance
        ORDER BY distance
        LIMIT 1
        RETURN p
        """
        
        start = session.run(start_query, lat=start_lat, lng=start_lng).single()
        if not start:
            return []
        
        # Find places within 2km using NEAR relationships
        itinerary_query = """
        MATCH (start:Place {id: $start_id})-[n:NEAR*1..2]-(p:Place)
        WHERE p.rating >= 4.0
          AND n[0].distance_km <= 2
        WITH DISTINCT p, min(n[0].distance_km) as min_distance
        RETURN p.name, p.category, p.rating, p.address, min_distance
        ORDER BY min_distance, p.rating DESC
        LIMIT 10
        """
        
        result = session.run(itinerary_query, start_id=start['p']['id'])
        return [dict(record) for record in result]


# USE CASE 4: Category Explorer
def explore_category(category_name, min_photos=10):
    """
    Explore all places in a category with rich media
    
    Args:
        category_name: e.g., "coffee", "hotel", "restaurant"
        min_photos: minimum number of photos
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WHERE toLower(p.category) CONTAINS toLower($category)
              AND p.photos_count >= $min_photos
            OPTIONAL MATCH (p)-[:HAS_REVIEW]->(r:Review)
            WITH p, collect(r.text)[0..2] as sample_reviews
            RETURN p.name, p.rating, p.category, p.photos_count,
                   p.address, p.description, sample_reviews
            ORDER BY p.rating DESC, p.photos_count DESC
        """, category=category_name, min_photos=min_photos)
        
        return [dict(record) for record in result]


# USE CASE 5: Find Similar Places
def find_similar_places(place_name, similarity_criteria='category'):
    """
    Find places similar to a given place
    
    Args:
        place_name: name of reference place
        similarity_criteria: 'category', 'location', or 'rating'
    """
    with driver.session() as session:
        if similarity_criteria == 'location':
            # Find nearby places
            query = """
            MATCH (p:Place {name: $name})-[n:NEAR]-(similar:Place)
            WHERE n.distance_km <= 1
            RETURN similar.name, similar.category, similar.rating, n.distance_km
            ORDER BY n.distance_km
            LIMIT 10
            """
        else:
            # Find same category
            query = """
            MATCH (p:Place {name: $name})
            MATCH (similar:Place)
            WHERE similar.category = p.category
              AND similar.id <> p.id
            RETURN similar.name, similar.rating, similar.address, similar.photos_count
            ORDER BY similar.rating DESC
            LIMIT 10
            """
        
        result = session.run(query, name=place_name)
        return [dict(record) for record in result]


# USE CASE 6: Aggregate Statistics
def get_area_statistics(center_lat, center_lng, radius_km=5):
    """
    Get tourism statistics for an area
    
    Args:
        center_lat, center_lng: center point
        radius_km: analysis radius
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WITH p, point.distance(
                point({latitude: $lat, longitude: $lng}),
                point({latitude: p.latitude, longitude: p.longitude})
            ) / 1000.0 as distance_km
            WHERE distance_km <= $radius
            WITH p, distance_km
            RETURN 
                count(p) as total_places,
                avg(p.rating) as avg_rating,
                sum(p.photos_count) as total_photos,
                sum(p.reviews_count) as total_reviews,
                collect(DISTINCT p.category)[0..10] as top_categories
        """, lat=center_lat, lng=center_lng, radius=radius_km)
        
        return dict(result.single())


# USE CASE 7: Review Sentiment Analysis (Simple)
def get_highly_reviewed_places(min_reviews=5):
    """
    Get places with most positive reviews
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)-[:HAS_REVIEW]->(r:Review)
            WHERE r.rating >= 4
            WITH p, count(r) as positive_reviews, avg(r.rating) as avg_review_rating
            WHERE positive_reviews >= $min_reviews
            RETURN p.name, p.rating, positive_reviews, avg_review_rating,
                   p.category, p.address
            ORDER BY positive_reviews DESC, avg_review_rating DESC
            LIMIT 20
        """, min_reviews=min_reviews)
        
        return [dict(record) for record in result]


def main():
    """Demo of all use cases"""
    print("="*80)
    print("DANANG TOURISM DATABASE - USE CASE DEMONSTRATIONS")
    print("="*80)
    
    # USE CASE 1
    print("\n1. HOTEL RECOMMENDATIONS (Near beach, 4+ rating)")
    print("-" * 80)
    hotels = recommend_hotels(min_rating=4.0, near_beach=True)
    for i, hotel in enumerate(hotels[:5], 1):
        print(f"{i}. {hotel['name']}")
        print(f"   Rating: {hotel['rating']}⭐ | Price: {hotel['price_range']}")
        print(f"   Beach: {hotel['beach_distance']:.1f}km | Photos: {hotel['photos']}")
    
    # USE CASE 2
    print("\n2. RESTAURANTS NEAR MY AN BEACH")
    print("-" * 80)
    restaurants = find_restaurants_nearby(16.0486, 108.2478, max_distance_km=1)
    for r in restaurants[:5]:
        print(f"- {r['p.name']}: {r['p.rating']}⭐ ({r['distance_km']:.2f}km)")
    
    # USE CASE 4
    print("\n3. COFFEE SHOPS WITH PHOTOS")
    print("-" * 80)
    cafes = explore_category('coffee', min_photos=15)
    for cafe in cafes[:5]:
        print(f"- {cafe['p.name']}: {cafe['p.rating']}⭐ ({cafe['p.photos_count']} photos)")
    
    # USE CASE 6
    print("\n4. AREA STATISTICS (5km radius from city center)")
    print("-" * 80)
    stats = get_area_statistics(16.0544, 108.2022, radius_km=5)
    print(f"Total Places: {stats['total_places']}")
    print(f"Average Rating: {stats['avg_rating']:.2f}⭐")
    print(f"Total Photos: {stats['total_photos']}")
    print(f"Top Categories: {', '.join(stats['top_categories'][:5])}")
    
    driver.close()


if __name__ == '__main__':
    main()
