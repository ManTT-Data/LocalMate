"""
Neo4j Service - Query place details from graph database
Provides rich relational data: nearby places, same category, photos, reviews
"""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


@dataclass
class NearbyPlace:
    """Nearby place with distance"""
    place_id: str
    name: str
    category: str
    rating: float
    distance_km: float


@dataclass
class Review:
    """Place review"""
    text: str
    rating: int
    reviewer: str


@dataclass
class PlaceDetails:
    """Complete place details from Neo4j"""
    place_id: str
    name: str
    category: str
    rating: float
    address: str
    phone: Optional[str]
    website: Optional[str]
    google_maps_url: Optional[str]
    description: Optional[str]
    specialty: Optional[str]
    price_range: Optional[str]
    coordinates: Dict[str, float]
    photos_count: int
    reviews_count: int
    photos: List[str] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    nearby_places: List[NearbyPlace] = field(default_factory=list)
    same_category: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        result = asdict(self)
        result['reviews'] = [asdict(r) for r in self.reviews]
        result['nearby_places'] = [asdict(n) for n in self.nearby_places]
        return result


class Neo4jService:
    """Service for querying Neo4j graph database"""
    
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, username, password]):
            raise ValueError("Missing Neo4j credentials in environment variables")
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        print("✅ Connected to Neo4j")
    
    def get_place_details(self, place_id: str) -> Optional[PlaceDetails]:
        """
        Get complete place details including photos, reviews, and relationships
        
        Args:
            place_id: The place identifier (slug)
            
        Returns:
            PlaceDetails object or None if not found
        """
        with self.driver.session() as session:
            # Main place query
            result = session.run("""
                MATCH (p:Place {id: $place_id})
                OPTIONAL MATCH (p)-[:HAS_PHOTO]->(photo:Photo)
                OPTIONAL MATCH (p)-[:HAS_REVIEW]->(review:Review)
                RETURN p,
                       collect(DISTINCT photo.path) as photos,
                       collect(DISTINCT {
                           text: review.text,
                           rating: review.rating,
                           reviewer: review.reviewer
                       }) as reviews
            """, place_id=place_id)
            
            record = result.single()
            if not record or not record['p']:
                return None
            
            place = record['p']
            
            # Build PlaceDetails
            details = PlaceDetails(
                place_id=place.get('id', place_id),
                name=place.get('name', 'Unknown'),
                category=place.get('category', ''),
                rating=float(place.get('rating', 0) or 0),
                address=place.get('address', ''),
                phone=place.get('phone'),
                website=place.get('website'),
                google_maps_url=place.get('google_maps_url'),
                description=place.get('description'),
                specialty=place.get('specialty'),
                price_range=place.get('price_range'),
                coordinates={
                    'lat': float(place.get('latitude', 0) or 0),
                    'lng': float(place.get('longitude', 0) or 0)
                },
                photos_count=int(place.get('photos_count', 0) or 0),
                reviews_count=int(place.get('reviews_count', 0) or 0),
                photos=record['photos'][:10],  # Limit photos
                reviews=[
                    Review(
                        text=r['text'] or '',
                        rating=int(r['rating'] or 0),
                        reviewer=r['reviewer'] or ''
                    ) for r in record['reviews'][:5]  # Top 5 reviews
                    if r['text']
                ]
            )
            
            return details
    
    def get_nearby_places(
        self, 
        place_id: str, 
        limit: int = 5,
        max_distance_km: float = 2.0
    ) -> List[NearbyPlace]:
        """
        Get places near a given place using NEAR relationship
        
        Args:
            place_id: The source place identifier
            limit: Maximum number of results
            max_distance_km: Maximum distance in km
            
        Returns:
            List of NearbyPlace objects
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Place {id: $place_id})-[n:NEAR]-(other:Place)
                WHERE n.distance_km <= $max_distance
                RETURN other.id as place_id,
                       other.name as name,
                       other.category as category,
                       other.rating as rating,
                       n.distance_km as distance_km
                ORDER BY n.distance_km
                LIMIT $limit
            """, place_id=place_id, max_distance=max_distance_km, limit=limit)
            
            nearby = []
            for record in result:
                nearby.append(NearbyPlace(
                    place_id=record['place_id'],
                    name=record['name'],
                    category=record['category'] or '',
                    rating=float(record['rating'] or 0),
                    distance_km=round(float(record['distance_km'] or 0), 2)
                ))
            
            return nearby
    
    def get_same_category_places(
        self, 
        place_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get other places in the same category
        
        Args:
            place_id: The source place identifier
            limit: Maximum number of results
            
        Returns:
            List of places in same category, ordered by rating
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Place {id: $place_id})-[:IN_CATEGORY]->(c:Category)<-[:IN_CATEGORY]-(other:Place)
                WHERE other.id <> $place_id
                RETURN other.id as place_id,
                       other.name as name,
                       other.category as category,
                       other.rating as rating,
                       other.address as address
                ORDER BY other.rating DESC
                LIMIT $limit
            """, place_id=place_id, limit=limit)
            
            places = []
            for record in result:
                places.append({
                    'place_id': record['place_id'],
                    'name': record['name'],
                    'category': record['category'] or '',
                    'rating': float(record['rating'] or 0),
                    'address': record['address'] or ''
                })
            
            return places
    
    def get_place_with_enrichment(
        self, 
        place_id: str,
        include_nearby: bool = True,
        include_same_category: bool = True,
        nearby_limit: int = 5
    ) -> Optional[PlaceDetails]:
        """
        Get place details with all enrichment data
        
        Args:
            place_id: The place identifier
            include_nearby: Whether to include nearby places
            include_same_category: Whether to include same category places
            nearby_limit: Limit for nearby/related results
            
        Returns:
            Fully enriched PlaceDetails or None
        """
        details = self.get_place_details(place_id)
        
        if not details:
            return None
        
        if include_nearby:
            details.nearby_places = self.get_nearby_places(place_id, limit=nearby_limit)
        
        if include_same_category:
            details.same_category = self.get_same_category_places(place_id, limit=nearby_limit)
        
        return details
    
    def search_by_location(
        self,
        lat: float,
        lng: float,
        radius_km: float = 2.0,
        limit: int = 10
    ) -> List[NearbyPlace]:
        """
        Search places near a GPS coordinate
        
        Args:
            lat: Latitude
            lng: Longitude
            radius_km: Search radius in km
            limit: Maximum results
            
        Returns:
            List of places with distances
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Place)
                WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
                WITH p, point.distance(
                    point({latitude: $lat, longitude: $lng}),
                    point({latitude: p.latitude, longitude: p.longitude})
                ) / 1000.0 as distance_km
                WHERE distance_km <= $radius
                RETURN p.id as place_id,
                       p.name as name,
                       p.category as category,
                       p.rating as rating,
                       distance_km
                ORDER BY distance_km
                LIMIT $limit
            """, lat=lat, lng=lng, radius=radius_km, limit=limit)
            
            places = []
            for record in result:
                places.append(NearbyPlace(
                    place_id=record['place_id'],
                    name=record['name'],
                    category=record['category'] or '',
                    rating=float(record['rating'] or 0),
                    distance_km=round(record['distance_km'], 2)
                ))
            
            return places
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()


# Test
if __name__ == "__main__":
    service = Neo4jService()
    
    # Test with a sample place
    print("=" * 60)
    print("🧪 NEO4J SERVICE TEST")
    print("=" * 60)
    
    # Get a place ID from database
    with service.driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WHERE p.rating >= 4.5
            RETURN p.id as place_id, p.name as name
            LIMIT 1
        """)
        record = result.single()
        
        if record:
            test_id = record['place_id']
            print(f"\n📍 Testing with: {record['name']} ({test_id})")
            
            # Get full details
            details = service.get_place_with_enrichment(test_id)
            if details:
                print(f"\n✅ Place Details:")
                print(f"   Name: {details.name}")
                print(f"   Category: {details.category}")
                print(f"   Rating: {details.rating}⭐")
                print(f"   Photos: {details.photos_count}")
                print(f"   Reviews: {len(details.reviews)}")
                
                print(f"\n📍 Nearby Places ({len(details.nearby_places)}):")
                for p in details.nearby_places[:3]:
                    print(f"   - {p.name} ({p.distance_km}km)")
                
                print(f"\n🏷️ Same Category ({len(details.same_category)}):")
                for p in details.same_category[:3]:
                    print(f"   - {p['name']} ({p['rating']}⭐)")
    
    # Test location search
    print("\n📍 Places near My An Beach (16.048, 108.247):")
    nearby = service.search_by_location(16.048, 108.247, radius_km=1)
    for p in nearby[:5]:
        print(f"   - {p.name} ({p.distance_km}km)")
    
    service.close()
    print("\n✅ Test complete!")
