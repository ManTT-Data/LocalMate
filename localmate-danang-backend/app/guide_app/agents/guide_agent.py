"""Guide Agent - generates place content using LLM and DB."""

import json
import re
from dataclasses import dataclass

from app.shared.constants.prompts.guide_prompts import (
    GUIDE_FUN_FACT_PROMPT,
    GUIDE_LOCAL_TIPS_PROMPT,
    GUIDE_FULL_CONTENT_PROMPT,
)
from app.shared.integrations.gemini_client import GeminiClient, gemini_client
from app.shared.integrations.neo4j_client import neo4j_client


@dataclass
class PlaceInfo:
    """Place information from database."""
    place_id: str
    name: str
    category: str = "unknown"
    rating: float = 0.0
    description: str = ""


class GuideAgent:
    """
    Agent for generating guide content.

    Fetches place info from Neo4j and generates content with LLM.
    """

    def __init__(self, llm: GeminiClient | None = None):
        """Initialize with optional LLM override."""
        self._llm = llm or gemini_client

    async def get_place_info(self, place_id: str) -> PlaceInfo:
        """
        Fetch place information from Neo4j database.

        Args:
            place_id: Place identifier

        Returns:
            PlaceInfo with details from database
        """
        try:
            query = """
            MATCH (p:Place {id: $place_id})
            RETURN p.id AS place_id, p.name AS name, 
                   p.category AS category, p.rating AS rating,
                   p.description AS description
            LIMIT 1
            """
            results = await neo4j_client.run_cypher(query, {"place_id": place_id})
            
            if results:
                r = results[0]
                return PlaceInfo(
                    place_id=r.get("place_id", place_id),
                    name=r.get("name", place_id),
                    category=r.get("category", "unknown"),
                    rating=r.get("rating", 0.0) or 0.0,
                    description=r.get("description", "") or "",
                )
        except Exception:
            pass
        
        # Fallback if DB fails
        return PlaceInfo(place_id=place_id, name=place_id)

    async def generate_guide_content(
        self,
        place_id: str,
        place_name: str | None = None,
    ) -> dict:
        """
        Generate full guide content for a place.

        Args:
            place_id: Place identifier
            place_name: Optional place name (will fetch from DB if not provided)

        Returns:
            Dict with fun_fact, tips, best_time_to_visit, suggested_duration, highlights
        """
        # Fetch place info from DB
        place_info = await self.get_place_info(place_id)
        
        # Override name if provided
        if place_name:
            place_info.name = place_name

        # Generate content using LLM
        prompt = GUIDE_FULL_CONTENT_PROMPT.format(
            place_id=place_info.place_id,
            place_name=place_info.name,
            category=place_info.category,
            rating=place_info.rating,
            description=place_info.description or "Địa điểm du lịch tại Đà Nẵng",
        )

        response = await self._llm.generate(prompt, temperature=0.7)

        # Parse JSON response
        try:
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)
            
            return {
                "place_id": place_info.place_id,
                "place_name": place_info.name,
                "category": place_info.category,
                "rating": place_info.rating,
                "fun_fact": data.get("fun_fact", ""),
                "tips": data.get("tips", []),
                "best_time_to_visit": data.get("best_time_to_visit", ""),
                "suggested_duration": data.get("suggested_duration", ""),
                "highlights": data.get("highlights", []),
            }
        except json.JSONDecodeError:
            # Fallback content
            return {
                "place_id": place_info.place_id,
                "place_name": place_info.name,
                "category": place_info.category,
                "rating": place_info.rating,
                "fun_fact": response.strip()[:200],
                "tips": [],
                "best_time_to_visit": "",
                "suggested_duration": "",
                "highlights": [],
            }


# Singleton instance
guide_agent = GuideAgent()
