#!/usr/bin/env python3
"""
Import Danang tourism data to Neo4j AuraDB
Creates graph with Places, Photos, Reviews, Categories, and spatial relationships
"""

from neo4j import GraphDatabase
import json
import os
import argparse
from pathlib import Path
import math
from collections import defaultdict

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")
    
    def create_constraints(self):
        """Create constraints and indexes"""
        with self.driver.session() as session:
            queries = [
                "CREATE CONSTRAINT place_id IF NOT EXISTS FOR (p:Place) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT photo_id IF NOT EXISTS FOR (p:Photo) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT review_id IF NOT EXISTS FOR (r:Review) REQUIRE r.id IS UNIQUE",
                "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
                "CREATE INDEX place_name IF NOT EXISTS FOR (p:Place) ON (p.name)",
                "CREATE INDEX place_category IF NOT EXISTS FOR (p:Place) ON (p.category)",
                "CREATE INDEX place_rating IF NOT EXISTS FOR (p:Place) ON (p.rating)",
            ]
            
            for query in queries:
                try:
                    session.run(query)
                except:
                    pass  # Constraint may already exist
            
            print("✅ Constraints and indexes created")
    
    def import_place(self, place_data, place_slug):
        """Import a single place with photos and reviews"""
        with self.driver.session() as session:
            # Extract data
            excel = place_data.get('excel_data', {})
            crawled = place_data.get('crawled_data', {})
            coords = crawled.get('coordinates', {})
            photos_data = place_data.get('photos', {})
            reviews_data = place_data.get('reviews', {})
            
            # Create Place node
            place_query = """
            MERGE (p:Place {id: $id})
            SET p.name = $name,
                p.name_vi = $name_vi,
                p.rating = $rating,
                p.category = $category,
                p.price_range = $price_range,
                p.description = $description,
                p.specialty = $specialty,
                p.latitude = $latitude,
                p.longitude = $longitude,
                p.address = $address,
                p.phone = $phone,
                p.website = $website,
                p.google_maps_url = $google_maps_url,
                p.source_file = $source_file,
                p.photos_count = $photos_count,
                p.reviews_count = $reviews_count
            RETURN p
            """
            
            session.run(place_query, {
                'id': place_slug,
                'name': crawled.get('name', excel.get('name', '')),
                'name_vi': excel.get('name', ''),
                'rating': crawled.get('rating'),
                'category': crawled.get('category', ''),
                'price_range': excel.get('price', ''),
                'description': excel.get('description', ''),
                'specialty': excel.get('specialty', ''),
                'latitude': coords.get('lat'),
                'longitude': coords.get('lng'),
                'address': crawled.get('address', ''),
                'phone': crawled.get('phone', ''),
                'website': crawled.get('website', ''),
                'google_maps_url': place_data.get('metadata', {}).get('google_maps_url', ''),
                'source_file': excel.get('source_file', ''),
                'photos_count': photos_data.get('count', 0),
                'reviews_count': reviews_data.get('count', 0)
            })
            
            # Create Category node and relationship
            if crawled.get('category'):
                category_query = """
                MERGE (c:Category {name: $category})
                WITH c
                MATCH (p:Place {id: $place_id})
                MERGE (p)-[:IN_CATEGORY]->(c)
                """
                session.run(category_query, {
                    'category': crawled.get('category'),
                    'place_id': place_slug
                })
            
            # Create Photo nodes
            photo_files = photos_data.get('files', [])
            for idx, filename in enumerate(photo_files[:30]):  # Limit to 30
                photo_query = """
                MERGE (ph:Photo {id: $photo_id})
                SET ph.filename = $filename,
                    ph.path = $path,
                    ph.order = $order
                WITH ph
                MATCH (p:Place {id: $place_id})
                MERGE (p)-[:HAS_PHOTO]->(ph)
                """
                session.run(photo_query, {
                    'photo_id': f"{place_slug}_{filename}",
                    'filename': filename,
                    'path': f"{place_slug}/photos/{filename}",
                    'order': idx + 1,
                    'place_id': place_slug
                })
            
            # Create Review nodes
            reviews = reviews_data.get('data', [])
            for idx, review in enumerate(reviews[:20]):  # Limit to 20
                review_query = """
                MERGE (r:Review {id: $review_id})
                SET r.reviewer = $reviewer,
                    r.rating = $rating,
                    r.text = $text
                WITH r
                MATCH (p:Place {id: $place_id})
                MERGE (p)-[:HAS_REVIEW]->(r)
                """
                session.run(review_query, {
                    'review_id': f"{place_slug}_review_{idx}",
                    'reviewer': review.get('reviewer', 'Anonymous'),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', ''),
                    'place_id': place_slug
                })
    
    def create_spatial_relationships(self, distance_km=2.0):
        """Create NEAR relationships based on distance"""
        print(f"\n📍 Creating spatial relationships (within {distance_km}km)...")
        
        with self.driver.session() as session:
            # Get all places with coordinates
            places = session.run("""
                MATCH (p:Place)
                WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
                RETURN p.id as id, p.latitude as lat, p.longitude as lng, p.name as name
            """).data()
            
            total = len(places)
            relationships_created = 0
            
            # Calculate distances and create relationships
            for i, p1 in enumerate(places):
                if (i + 1) % 50 == 0:
                    print(f"   Processing {i+1}/{total} places...")
                
                for p2 in places[i+1:]:  # Avoid duplicates
                    dist = self._haversine_distance(
                        p1['lat'], p1['lng'],
                        p2['lat'], p2['lng']
                    )
                    
                    if dist <= distance_km:
                        session.run("""
                            MATCH (p1:Place {id: $id1})
                            MATCH (p2:Place {id: $id2})
                            MERGE (p1)-[n:NEAR]->(p2)
                            SET n.distance_km = $distance
                            MERGE (p2)-[n2:NEAR]->(p1)
                            SET n2.distance_km = $distance
                        """, {
                            'id1': p1['id'],
                            'id2': p2['id'],
                            'distance': round(dist, 2)
                        })
                        relationships_created += 2
            
            print(f"✅ Created {relationships_created} NEAR relationships")
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in km between two coordinates"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_statistics(self):
        """Get database statistics"""
        with self.driver.session() as session:
            stats = {}
            
            # Node counts
            stats['places'] = session.run("MATCH (p:Place) RETURN count(p) as count").single()['count']
            stats['photos'] = session.run("MATCH (p:Photo) RETURN count(p) as count").single()['count']
            stats['reviews'] = session.run("MATCH (r:Review) RETURN count(r) as count").single()['count']
            stats['categories'] = session.run("MATCH (c:Category) RETURN count(c) as count").single()['count']
            
            # Relationship counts
            stats['near'] = session.run("MATCH ()-[n:NEAR]->() RETURN count(n) as count").single()['count']
            stats['has_photo'] = session.run("MATCH ()-[r:HAS_PHOTO]->() RETURN count(r) as count").single()['count']
            stats['has_review'] = session.run("MATCH ()-[r:HAS_REVIEW]->() RETURN count(r) as count").single()['count']
            
            return stats

def main():
    parser = argparse.ArgumentParser(description='Import Danang tourism data to Neo4j AuraDB')
    parser.add_argument('--uri', required=True, help='Neo4j connection URI (neo4j+s://...)')
    parser.add_argument('--user', default='neo4j', help='Username')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--data-dir', default='data/places', help='Directory with merged data')
    parser.add_argument('--clear', action='store_true', help='Clear database before import')
    parser.add_argument('--skip-spatial', action='store_true', help='Skip spatial relationships (faster)')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🚀 NEO4J AURADB IMPORT - DANANG TOURISM")
    print("="*80)
    
    # Connect to Neo4j
    print(f"\n📡 Connecting to {args.uri}...")
    importer = Neo4jImporter(args.uri, args.user, args.password)
    
    try:
        # Clear if requested
        if args.clear:
            print("\n⚠️  Clearing existing data...")
            importer.clear_database()
        
        # Create constraints
        print("\n🔧 Setting up constraints...")
        importer.create_constraints()
        
        # Import places
        print(f"\n📥 Importing places from {args.data_dir}...")
        
        places_dir = Path(args.data_dir)
        if not places_dir.exists():
            print(f"❌ Error: {args.data_dir} not found. Run merge_data.py first!")
            return
        
        place_folders = [d for d in places_dir.iterdir() if d.is_dir()]
        total = len(place_folders)
        
        for idx, place_folder in enumerate(place_folders, 1):
            json_file = place_folder / 'place_data.json'
            if not json_file.exists():
                continue
            
            with open(json_file, 'r', encoding='utf-8') as f:
                place_data = json.load(f)
            
            place_slug = place_folder.name
            importer.import_place(place_data, place_slug)
            
            if idx % 10 == 0:
                print(f"   Imported {idx}/{total} places...")
        
        print(f"✅ Imported {total} places")
        
        # Create spatial relationships
        if not args.skip_spatial:
            importer.create_spatial_relationships(distance_km=2.0)
        
        # Get statistics
        print("\n📊 DATABASE STATISTICS:")
        print("="*80)
        stats = importer.get_statistics()
        
        print(f"\nNodes:")
        print(f"  Places:     {stats['places']:,}")
        print(f"  Photos:     {stats['photos']:,}")
        print(f"  Reviews:    {stats['reviews']:,}")
        print(f"  Categories: {stats['categories']:,}")
        print(f"  TOTAL:      {sum([stats['places'], stats['photos'], stats['reviews'], stats['categories']]):,}")
        
        print(f"\nRelationships:")
        print(f"  NEAR:       {stats['near']:,}")
        print(f"  HAS_PHOTO:  {stats['has_photo']:,}")
        print(f"  HAS_REVIEW: {stats['has_review']:,}")
        print(f"  TOTAL:      {sum([stats['near'], stats['has_photo'], stats['has_review']]):,}")
        
        print("\n" + "="*80)
        print("✅ IMPORT COMPLETE!")
        print("="*80)
        print(f"\n🌐 Access your database:")
        print(f"   URL: https://console.neo4j.io")
        print(f"   Username: {args.user}")
        print("\n💡 Try sample queries in Neo4j Browser!")
        
    finally:
        importer.close()

if __name__ == '__main__':
    main()
