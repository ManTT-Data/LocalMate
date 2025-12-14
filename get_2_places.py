"""
Get complete information for any 2 places from the database
"""

from neo4j import GraphDatabase
import json

# Connection
URI = "neo4j+s://64ff7b02.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def get_complete_place_info(place_name):
    """
    Get ALL information for a place including photos, reviews, and nearby places
    
    Args:
        place_name: Name of the place (exact match)
    
    Returns:
        dict with all place information
    """
    with driver.session() as session:
        # Get place with all relationships
        result = session.run("""
            MATCH (p:Place)
            WHERE p.name = $name
            
            // Get category
            OPTIONAL MATCH (p)-[:IN_CATEGORY]->(c:Category)
            
            // Get photos
            OPTIONAL MATCH (p)-[:HAS_PHOTO]->(photo:Photo)
            
            // Get reviews
            OPTIONAL MATCH (p)-[:HAS_REVIEW]->(review:Review)
            
            // Get nearby places (within 1km)
            OPTIONAL MATCH (p)-[n:NEAR]-(nearby:Place)
            WHERE n.distance_km <= 1
            
            RETURN p,
                   c.name as category_name,
                   collect(DISTINCT {
                       filename: photo.filename,
                       path: photo.path,
                       order: photo.order
                   }) as photos,
                   collect(DISTINCT {
                       reviewer: review.reviewer,
                       rating: review.rating,
                       text: review.text
                   }) as reviews,
                   collect(DISTINCT {
                       name: nearby.name,
                       category: nearby.category,
                       rating: nearby.rating,
                       distance_km: n.distance_km
                   }) as nearby_places
        """, name=place_name)
        
        record = result.single()
        if not record:
            return None
        
        # Format the complete information
        place = record['p']
        return {
            # Basic Info
            'id': place['id'],
            'name': place['name'],
            'name_vi': place.get('name_vi'),
            'rating': place.get('rating'),
            'category': place.get('category'),
            'category_name': record['category_name'],
            
            # Location
            'address': place.get('address'),
            'coordinates': {
                'latitude': place.get('latitude'),
                'longitude': place.get('longitude')
            },
            
            # Contact
            'phone': place.get('phone'),
            'website': place.get('website'),
            'google_maps_url': place.get('google_maps_url'),
            
            # Descriptions (from Excel)
            'price_range': place.get('price_range'),
            'description': place.get('description'),
            'specialty': place.get('specialty'),
            
            # Stats
            'photos_count': place.get('photos_count', 0),
            'reviews_count': place.get('reviews_count', 0),
            
            # Media
            'photos': [p for p in record['photos'] if p['filename']],
            'reviews': [r for r in record['reviews'] if r['reviewer']],
            
            # Nearby
            'nearby_places': [n for n in record['nearby_places'] if n['name']][:10]
        }


def get_random_places(count=2):
    """
    Get random places from database
    
    Args:
        count: number of random places to get
    
    Returns:
        list of place names
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WHERE p.rating >= 4.0
            RETURN p.name
            ORDER BY rand()
            LIMIT $count
        """, count=count)
        
        return [record['p.name'] for record in result]


def main():
    """
    Demo: Get complete info for 2 random places
    """
    print("="*80)
    print("GETTING COMPLETE INFORMATION FOR 2 RANDOM PLACES")
    print("="*80)
    
    # Get 2 random place names
    place_names = get_random_places(2)
    
    all_data = []
    
    for i, place_name in enumerate(place_names, 1):
        print(f"\n{'='*80}")
        print(f"PLACE {i}: {place_name}")
        print("="*80)
        
        # Get complete information
        info = get_complete_place_info(place_name)
        
        if info:
            all_data.append(info)
            
            # Print formatted information
            print(f"\n📍 BASIC INFO")
            print(f"   Name: {info['name']}")
            print(f"   Vietnamese: {info['name_vi']}")
            print(f"   Rating: {info['rating']}⭐")
            print(f"   Category: {info['category']}")
            
            print(f"\n🗺️  LOCATION")
            print(f"   Address: {info['address']}")
            print(f"   Coordinates: {info['coordinates']['latitude']}, {info['coordinates']['longitude']}")
            
            print(f"\n📞 CONTACT")
            print(f"   Phone: {info['phone'] or 'N/A'}")
            print(f"   Website: {info['website'] or 'N/A'}")
            
            print(f"\n📝 DETAILS")
            print(f"   Price Range: {info['price_range'] or 'N/A'}")
            print(f"   Description: {info['description'] or 'N/A'}")
            print(f"   Specialty: {info['specialty'] or 'N/A'}")
            
            print(f"\n📸 MEDIA")
            print(f"   Photos: {info['photos_count']} total")
            if info['photos'][:3]:
                print(f"   Sample files:")
                for photo in info['photos'][:3]:
                    print(f"      - {photo['filename']}")
            
            print(f"\n💬 REVIEWS")
            print(f"   Total: {info['reviews_count']} reviews")
            if info['reviews'][:2]:
                print(f"   Sample reviews:")
                for review in info['reviews'][:2]:
                    print(f"      - {review['reviewer']}: {review['rating']}⭐")
                    print(f"        \"{review['text'][:100]}...\"")
            
            print(f"\n🔗 NEARBY PLACES")
            print(f"   Found {len(info['nearby_places'])} places within 1km:")
            for nearby in info['nearby_places'][:5]:
                print(f"      - {nearby['name']}: {nearby['rating']}⭐ ({nearby['distance_km']:.2f}km)")
        else:
            print(f"   ❌ Place not found!")
    
    # Save to JSON
    output_file = 'sample_2_places.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ Complete data saved to: {output_file}")
    print(f"   Total places: {len(all_data)}")
    print(f"   Total photos: {sum(p['photos_count'] for p in all_data)}")
    print(f"   Total reviews: {sum(p['reviews_count'] for p in all_data)}")
    print("="*80)
    
    driver.close()


if __name__ == '__main__':
    main()
