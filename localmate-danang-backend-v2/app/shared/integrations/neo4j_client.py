"""Neo4j client for graph database operations."""

from neo4j import AsyncGraphDatabase

from app.core.config import settings


class Neo4jClient:
    """Async Neo4j client for spatial and graph queries."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j driver."""
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self) -> None:
        """Close the driver connection."""
        await self._driver.close()

    async def run_cypher(
        self,
        query: str,
        params: dict | None = None,
    ) -> list[dict]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            params: Optional query parameters

        Returns:
            List of result records as dictionaries
        """
        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            return await result.data()

    async def verify_connectivity(self) -> bool:
        """Verify connection to Neo4j."""
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception:
            return False


# Global Neo4j client instance
neo4j_client = Neo4jClient(
    settings.neo4j_uri,
    settings.neo4j_username,
    settings.neo4j_password,
)
