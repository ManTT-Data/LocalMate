#!/usr/bin/env python3
"""
Retry spatial relationships creation (separate from main import)
Use this if spatial import failed due to timeout
"""

from neo4j import GraphDatabase
import math

URI = "neo4j+s://64ff7b02.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def create_spatial_relationships(distance_km=2.0):
    """Create NEAR relationships with timeout handling"""
    print(f"📍 Creating spatial relationships (within {distance_km}km)...")
    
    with driver.session() as session:
        # Get all places
        places = session.run("""
            MATCH (p:Place)
            WHERE p.latitude IS NOT NULL AND p.longitude IS NOT NULL
            RETURN p.id as id, p.latitude as lat, p.longitude as lng
        """).data()
        
        total = len(places)
        print(f"   Found {total} places with coordinates")
        
        relationships_created = 0
        batch_size = 10  # Small batches to avoid timeout
        
        # Process in batches
        for i in range(0, len(places), batch_size):
            batch = places[i:i+batch_size]
            
            for p1 in batch:
                # Find nearby places
                nearby = []
                for p2 in places:
                    if p1['id'] != p2['id']:
                        dist = haversine_distance(
                            p1['lat'], p1['lng'],
                            p2['lat'], p2['lng']
                        )
                        if dist <= distance_km:
                            nearby.append((p2['id'], round(dist, 2)))
                
                # Create relationships in batch
                if nearby:
                    try:
                        with driver.session() as batch_session:
                            for p2_id, dist in nearby:
                                batch_session.run("""
                                    MATCH (p1:Place {id: $id1})
                                    MATCH (p2:Place {id: $id2})
                                    MERGE (p1)-[n:NEAR]->(p2)
                                    SET n.distance_km = $distance
                                """, id1=p1['id'], id2=p2_id, distance=dist)
                                relationships_created += 1
                    except Exception as e:
                        print(f"   ⚠️ Batch {i}-{i+batch_size} error: {str(e)[:50]}")
                        continue
            
            if (i + batch_size) % 50 == 0:
                print(f"   Processed {min(i+batch_size, total)}/{total} places...")
        
        print(f"✅ Created {relationships_created} NEAR relationships")

if __name__ == '__main__':
    try:
        create_spatial_relationships(distance_km=2.0)
    finally:
        driver.close()
