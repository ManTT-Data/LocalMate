"""
Extract 303 places from Neo4j or local JSON files
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from neo4j import GraphDatabase

from .models import PlaceData, Coordinates, Photo, Review, NearbyPlace
from .config import (
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD,
    PLACES_DIR, RAG_PROCESSED_DIR
)


class PlaceExtractor:
    """Extract and normalize place data from multiple sources"""
    
    def __init__(self):
        self.neo4j_driver = None
        if NEO4J_URI and NEO4J_PASSWORD:
            try:
                self.neo4j_driver = GraphDatabase.driver(
                    NEO4J_URI,
                    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
                )
                print("✅ Connected to Neo4j")
            except Exception as e:
                print(f"⚠️ Neo4j connection failed: {e}")
                print("📁 Will use local JSON files as fallback")
    
    def extract_all(self) -> List[PlaceData]:
        """
        Extract all places using best available source
        Merge Neo4j + JSON files to get complete dataset
        """
        all_places = {}  # Use dict to deduplicate by place_id
        
        # 1. Try Neo4j first
        if self.neo4j_driver:
            try:
                neo4j_places = self._extract_from_neo4j()
                for place in neo4j_places:
                    all_places[place.id] = place
                print(f"✅ Extracted {len(neo4j_places)} places from Neo4j")
            except Exception as e:
                print(f"⚠️ Neo4j extraction failed: {e}")
        
        # 2. Load from JSON files (to fill gaps)
        json_places = self._extract_from_json_files()
        for place in json_places:
            if place.id not in all_places:
                all_places[place.id] = place
        
        print(f"✅ Total unique places: {len(all_places)} (Neo4j + JSON files)")
        
        return list(all_places.values())
    
    def _extract_from_neo4j(self) -> List[PlaceData]:
        """Extract from Neo4j database"""
        query = """
        MATCH (p:Place)
        OPTIONAL MATCH (p)-[:HAS_REVIEW]->(r:Review)
        OPTIONAL MATCH (p)-[:HAS_PHOTO]->(ph:Photo)
        OPTIONAL MATCH (p)-[:NEAR]->(nearby:Place)
        WITH p, 
             collect(DISTINCT r) as reviews,
             collect(DISTINCT ph) as photos,
             collect(DISTINCT {
                 name: nearby.name,
                 rating: nearby.rating,
                 category: nearby.category,
                 distance: 1.0
             }) as nearby_places
        RETURN p, reviews, photos, nearby_places
        """
        
        places = []
        with self.neo4j_driver.session() as session:
            result = session.run(query)
            for record in result:
                place_node = record['p']
                reviews = record['reviews']
                photos = record['photos']
                nearby = record.get('nearby_places', [])
                
                # Convert to PlaceData
                place = self._neo4j_to_place_data(
                    place_node, reviews, photos, nearby
                )
                if place:
                    places.append(place)
        
        return places
    
    def _neo4j_to_place_data(self, node, reviews, photos, nearby) -> Optional[PlaceData]:
        """Convert Neo4j node to PlaceData"""
        try:
            # Handle missing coordinates
            latitude = node.get('latitude')
            longitude = node.get('longitude')
            if latitude is None or longitude is None:
                # Try to get from coordinates field
                coords = node.get('coordinates', {})
                latitude = coords.get('latitude', 0.0) if isinstance(coords, dict) else 0.0
                longitude = coords.get('longitude', 0.0) if isinstance(coords, dict) else 0.0
            
            # Handle missing rating
            rating = node.get('rating', 0)
            if rating is None:
                rating = 0.0
            
            return PlaceData(
                id=node.get('id', node.get('place_id', '')),
                name=node.get('name', 'Unknown'),
                name_vi=node.get('name_vi'),
                rating=float(rating),
                category=node.get('category', 'Unknown'),
                category_name=node.get('category_name', node.get('category', 'Unknown')),
                address=node.get('address', ''),
                coordinates=Coordinates(
                    latitude=float(latitude) if latitude else 0.0,
                    longitude=float(longitude) if longitude else 0.0
                ),
                phone=node.get('phone'),
                website=node.get('website'),
                google_maps_url=node.get('google_maps_url', ''),
                price_range=node.get('price_range'),
                description=node.get('description', ''),
                specialty=node.get('specialty', ''),
                photos_count=len(photos),
                reviews_count=len(reviews),
                photos=[
                    Photo(
                        path=ph.get('path', ''),
                        filename=ph.get('filename', ''),
                        order=ph.get('order', 0)
                    ) for ph in photos if ph.get('path')
                ],
                reviews=[
                    Review(
                        rating=int(r.get('rating', 0)) if r.get('rating') is not None else 0,
                        reviewer=r.get('reviewer', 'Anonymous'),
                        text=r.get('text', '')
                    ) for r in reviews if r.get('text')
                ],
                nearby_places=[
                    NearbyPlace(
                        distance_km=float(n.get('distance', 0)) if n.get('distance') else 0.0,
                        name=n.get('name', ''),
                        rating=float(n.get('rating', 0)) if n.get('rating') else 0.0,
                        category=n.get('category', '')
                    ) for n in nearby if n.get('name')
                ]
            )
        except Exception as e:
            print(f"⚠️ Failed to parse place {node.get('id', 'unknown')}: {e}")
            return None
    
    def _extract_from_json_files(self) -> List[PlaceData]:
        """Extract from local JSON files"""
        places = []
        
        # Check if we have sample_2_places.json first
        sample_file = Path(PLACES_DIR).parent / "sample_2_places.json"
        if sample_file.exists():
            print(f"📂 Loading from {sample_file}")
            with open(sample_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    place = self._json_to_place_data(item)
                    if place:
                        places.append(place)
        
        # Also scan data/places/ directory for individual place_data.json files
        places_dir = Path(PLACES_DIR)
        if places_dir.exists():
            for place_folder in places_dir.iterdir():
                if not place_folder.is_dir():
                    continue
                
                json_file = place_folder / "place_data.json"
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            place = self._json_to_place_data(data)
                            if place and not any(p.id == place.id for p in places):
                                places.append(place)
                    except Exception as e:
                        print(f"⚠️ Failed to load {json_file}: {e}")
        
        return places
    
    def _json_to_place_data(self, data: dict) -> Optional[PlaceData]:
        """Convert JSON dict to PlaceData"""
        try:
            # Handle photos - can be dict or string
            photos = []
            for photo in data.get('photos', []):
                if isinstance(photo, dict):
                    photos.append(Photo(**photo))
                elif isinstance(photo, str):
                    # Handle string format (just path)
                    photos.append(Photo(path=photo, filename=photo.split('/')[-1], order=len(photos)+1))
            
            # Handle reviews
            reviews = []
            for review in data.get('reviews', []):
                if isinstance(review, dict):
                    reviews.append(Review(**review))
            
            # Handle nearby places
            nearby = []
            for n in data.get('nearby_places', []):
                if isinstance(n, dict):
                    nearby.append(NearbyPlace(**n))
            
            return PlaceData(
                id=data.get('id', ''),
                name=data.get('name', 'Unknown'),
                name_vi=data.get('name_vi'),
                rating=float(data.get('rating', 0)),
                category=data.get('category', 'Unknown'),
                category_name=data.get('category_name', data.get('category', 'Unknown')),
                address=data.get('address', ''),
                coordinates=Coordinates(
                    latitude=data.get('coordinates', {}).get('latitude', 0),
                    longitude=data.get('coordinates', {}).get('longitude', 0)
                ),
                phone=data.get('phone'),
                website=data.get('website'),
                google_maps_url=data.get('google_maps_url', ''),
                price_range=data.get('price_range'),
                description=data.get('description', ''),
                specialty=data.get('specialty', ''),
                photos_count=data.get('photos_count', len(photos)),
                reviews_count=data.get('reviews_count', len(reviews)),
                photos=photos,
                reviews=reviews,
                nearby_places=nearby
            )
        except Exception as e:
            print(f"⚠️ Failed to parse JSON place {data.get('id', 'unknown')}: {e}")
            return None
    
    def save_normalized(self, places: List[PlaceData], output_file: str = "places_normalized.json"):
        """Save normalized places to JSON"""
        output_path = RAG_PROCESSED_DIR / output_file
        
        # Convert to serializable format
        data = []
        for place in places:
            data.append({
                'id': place.id,
                'name': place.name,
                'name_vi': place.name_vi,
                'rating': place.rating,
                'category': place.category,
                'address': place.address,
                'coordinates': {
                    'latitude': place.coordinates.latitude,
                    'longitude': place.coordinates.longitude
                },
                'phone': place.phone,
                'website': place.website,
                'google_maps_url': place.google_maps_url,
                'price_range': place.price_range,
                'description': place.description,
                'specialty': place.specialty,
                'photos_count': place.photos_count,
                'reviews_count': place.reviews_count,
                'tags': place.tags,
                'price_min': place.price_min,
                'price_max': place.price_max,
                'photos': [
                    {'path': p.path, 'filename': p.filename, 'order': p.order}
                    for p in place.photos
                ],
                'reviews': [
                    {'rating': r.rating, 'reviewer': r.reviewer, 'text': r.text}
                    for r in place.reviews
                ],
                'nearby_places': [
                    {
                        'distance_km': n.distance_km,
                        'name': n.name,
                        'rating': n.rating,
                        'category': n.category
                    }
                    for n in place.nearby_places
                ]
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(places)} normalized places to {output_path}")
        return output_path
    
    def close(self):
        """Close Neo4j connection"""
        if self.neo4j_driver:
            self.neo4j_driver.close()


if __name__ == "__main__":
    # Test extraction
    extractor = PlaceExtractor()
    places = extractor.extract_all()
    print(f"\n📊 Extracted {len(places)} places")
    
    if places:
        print(f"\n📍 Sample place: {places[0].name}")
        print(f"   Category: {places[0].category}")
        print(f"   Rating: {places[0].rating}")
        print(f"   Reviews: {places[0].reviews_count}")
        print(f"   Photos: {places[0].photos_count}")
        print(f"   Tags: {places[0].tags}")
        
        # Save normalized
        output = extractor.save_normalized(places)
        print(f"\n✅ Done! Output: {output}")
    
    extractor.close()
