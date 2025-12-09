# PHASE 4 – LLM Integration & Embeddings

## 🎯 Mục tiêu

Planner thực sự "thông minh" với **Gemini 2.5 Flash** và **semantic search**.

---

## 📦 Deliverables

| Item | Path |
|------|------|
| Gemini Client | `app/shared/integrations/gemini_client.py` |
| Embedding Client | `app/shared/integrations/embedding_client.py` |
| Planner Prompts | `app/shared/constants/prompts/planner_prompts.py` |
| RAG Pipeline | `app/shared/graph/rag_pipeline.py` |

---

## 📋 Tasks

### Task 4.1: Gemini Client (Enhanced)

**`app/shared/integrations/gemini_client.py`:**
```python
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.google_api_key)

class GeminiClient:
    def __init__(self, model: str = None):
        self.model = model or settings.gemini_model
    
    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        system_instruction: str | None = None,
    ) -> str:
        config = {"temperature": temperature}
        if system_instruction:
            config["system_instruction"] = system_instruction
        
        response = client.models.generate_content(
            model=self.model,
            contents=messages,
            config=config
        )
        return response.text
    
    async def parse_intent(self, user_query: str) -> dict:
        prompt = f'''Parse this travel query into structured format:
Query: "{user_query}"

Return JSON:
{{"categories": [...], "specialty": [...], "near": "...", "min_rating": 4.0}}'''
        
        response = await self.chat([{"role": "user", "parts": [prompt]}])
        # Parse JSON from response
        import json
        return json.loads(response)

gemini_client = GeminiClient()
```

---

### Task 4.2: Embedding Client

**`app/shared/integrations/embedding_client.py`:**
```python
from google import genai
import httpx
from app.core.config import settings

client = genai.Client(api_key=settings.google_api_key)

class EmbeddingClient:
    """Text: text-embedding-004, Image: CLIP via HuggingFace API"""
    
    async def embed_text(self, text: str) -> list[float]:
        """Generate 768-dim embedding using text-embedding-004."""
        response = client.models.embed_content(
            model=settings.embedding_model,
            contents=text
        )
        return response.embeddings[0].values
    
    async def embed_image(self, image_url: str) -> list[float]:
        """Generate 512-dim embedding using CLIP via HuggingFace."""
        async with httpx.AsyncClient() as http:
            response = await http.post(
                "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32",
                headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
                json={"inputs": image_url}
            )
            return response.json()
    
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple texts."""
        response = client.models.embed_content(
            model=settings.embedding_model,
            contents=texts
        )
        return [e.values for e in response.embeddings]

embedding_client = EmbeddingClient()
```

---

### Task 4.3: Semantic Search

**`app/shared/graph/semantic_search.py`:**
```python
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.integrations.embedding_client import embedding_client

async def search_places_semantic(
    db: AsyncSession,
    query: str,
    limit: int = 10,
    threshold: float = 0.7
) -> list[dict]:
    """Search places using text embedding similarity."""
    query_embedding = await embedding_client.embed_text(query)
    
    result = await db.execute(
        text("""
            SELECT place_id, metadata,
                   1 - (text_embedding <=> :embedding::vector) as similarity
            FROM place_embeddings
            WHERE 1 - (text_embedding <=> :embedding::vector) > :threshold
            ORDER BY text_embedding <=> :embedding::vector
            LIMIT :limit
        """),
        {"embedding": query_embedding, "threshold": threshold, "limit": limit}
    )
    return [dict(row) for row in result.fetchall()]
```

---

### Task 4.4: RAG Pipeline

**`app/shared/graph/rag_pipeline.py`:**
```python
from app.shared.integrations.gemini_client import gemini_client
from app.shared.graph.semantic_search import search_places_semantic
from app.shared.integrations.neo4j_client import neo4j_client

class RAGPipeline:
    async def find_places(self, db, query: str) -> list[dict]:
        """
        1. Parse intent with Gemini
        2. Semantic search in pgvector
        3. Enrich with Neo4j relationships
        """
        # Parse intent
        intent = await gemini_client.parse_intent(query)
        
        # Semantic search
        places = await search_places_semantic(db, query)
        
        # Enrich with Neo4j (get nearby places, relationships)
        enriched = []
        for place in places:
            neo4j_data = await neo4j_client.run_cypher(
                "MATCH (p:Place {id: $id}) RETURN p",
                {"id": place["place_id"]}
            )
            enriched.append({**place, "neo4j": neo4j_data[0] if neo4j_data else None})
        
        return enriched

rag_pipeline = RAGPipeline()
```

---

## ✅ Acceptance Criteria

| Criteria | Test |
|----------|------|
| Intent parsing | "seafood near beach" → correct JSON |
| Semantic search | Query returns relevant places |
| Embeddings stored | pgvector has place embeddings |

---

## ⏰ Estimated Time: 3-4 hours
