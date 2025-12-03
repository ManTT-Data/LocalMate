"""
Supabase Vector Client

Vector database cho embeddings và semantic search
"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.config import settings
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class SupabaseVectorClient:
    """Supabase vector database client"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase vector client initialized")
    
    async def upsert_embedding(
        self,
        table: str,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Upsert an embedding to the vector store
        
        Args:
            table: Table name (e.g., "place_embeddings")
            id: Unique identifier
            embedding: Embedding vector
            metadata: Additional metadata
            
        Returns:
            Upsert result
        """
        data = {
            "id": id,
            "embedding": embedding,
            **metadata,
        }
        
        result = self.client.table(table).upsert(data).execute()
        return result.data
    
    async def search_similar(
        self,
        table: str,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using vector similarity
        
        Args:
            table: Table name
            query_embedding: Query embedding vector
            limit: Maximum results
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar items with similarity scores
        """
        # This is a placeholder - actual implementation depends on Supabase pgvector setup
        # You would use: .rpc('match_places', {...}) with a custom function
        logger.warning("search_similar: Not fully implemented - needs pgvector RPC function")
        return []


# Global instance
vector_client = SupabaseVectorClient()
