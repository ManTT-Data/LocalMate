"""
Neo4j Graph Database Client

Kết nối và query Neo4j
"""

from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import settings
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class Neo4jClient:
    """Neo4j database client"""
    
    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
    
    async def connect(self):
        """Connect to Neo4j"""
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        logger.info("Connected to Neo4j")
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
    
    async def run_cypher(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run a Cypher query
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            await self.connect()
        
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records
    
    async def create_place_node(self, place_data: Dict[str, Any]) -> str:
        """
        Create a Place node in Neo4j
        
        Returns:
            Neo4j node ID
        """
        query = """
        CREATE (p:Place {
            id: $id,
            name: $name,
            latitude: $latitude,
            longitude: $longitude,
            category: $category,
            tags: $tags
        })
        RETURN elementId(p) as node_id
        """
        result = await self.run_cypher(query, place_data)
        return result[0]["node_id"] if result else None


# Global instance
neo4j_client = Neo4jClient()
