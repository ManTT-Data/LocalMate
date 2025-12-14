#!/usr/bin/env python3
"""
Create spatial relationships using Cypher batching (more efficient for AuraDB)
"""

from neo4j import GraphDatabase
import time

URI = "neo4j+s://64ff7b02.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "O-yclTiDYCKZCg55HfVoe1pPLNpZGwG0-UCoBzIS_c4"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def create_spatial_with_cypher(distance_km=2.0):
    """
    Create NEAR relationships using pure Cypher (server-side calculation)
    More efficient than Python client-side calculation
    """
    print(f"📍 Creating spatial relationships using Cypher (within {distance_km}km)...")
    
    with driver.session() as session:
        # First, count how many will be created
        count_query = """
        MATCH (p1:Place), (p2:Place)
        WHERE p1.latitude IS NOT NULL 
          AND p2.latitude IS NOT NULL
          AND id(p1) < id(p2)
          AND point.distance(
              point({latitude: p1.latitude, longitude: p1.longitude}),
              point({latitude: p2.latitude, longitude: p2.longitude})
          ) / 1000.0 <= $distance_km
        RETURN count(*) as total
        """
        
        result = session.run(count_query, distance_km=distance_km)
        total = result.single()['total']
        print(f"   Will create {total * 2} relationships (bidirectional)")
        
        # Create relationships in batches
        batch_size = 1000
        created = 0
        
        while True:
            create_query = """
            MATCH (p1:Place), (p2:Place)
            WHERE p1.latitude IS NOT NULL 
              AND p2.latitude IS NOT NULL
              AND id(p1) < id(p2)
              AND NOT EXISTS((p1)-[:NEAR]-(p2))
            WITH p1, p2, 
                 point.distance(
                     point({latitude: p1.latitude, longitude: p1.longitude}),
                     point({latitude: p2.latitude, longitude: p2.longitude})
                 ) / 1000.0 as distance_km
            WHERE distance_km <= $distance_km
            WITH p1, p2, distance_km
            LIMIT $batch_size
            
            CREATE (p1)-[n1:NEAR]->(p2)
            CREATE (p2)-[n2:NEAR]->(p1)
            SET n1.distance_km = round(distance_km * 100) / 100
            SET n2.distance_km = round(distance_km * 100) / 100
            
            RETURN count(*) as batch_count
            """
            
            result = session.run(create_query, 
                               distance_km=distance_km, 
                               batch_size=batch_size)
            
            batch_count = result.single()['batch_count']
            
            if batch_count == 0:
                break
            
            created += batch_count
            print(f"   Created {created}/{total} pairs ({created*2}/{total*2} relationships)...")
            
            # Small delay to avoid overwhelming server
            time.sleep(0.5)
        
        print(f"✅ Created {created * 2} NEAR relationships")

if __name__ == '__main__':
    print("Waiting 30 seconds for database to settle...")
    time.sleep(30)
    
    try:
        create_spatial_with_cypher(distance_km=2.0)
    finally:
        driver.close()
