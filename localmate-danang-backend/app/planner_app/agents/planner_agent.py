"""
Planner Agent

Main agent để tạo travel itinerary sử dụng Graph-RAG
"""

from typing import List, Dict, Any
from app.shared.graph.rag_pipeline import rag_pipeline
from app.shared.graph.pathfinding import nearest_neighbor_tsp, optimize_route_2opt
from app.shared.integrations.llm_client import llm_client
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    """AI Travel Planner Agent"""
    
    async def create_itinerary(
        self,
        duration_days: int,
        interests: List[str],
        budget: str,
        family_size: int,
        start_lat: float = 16.0544,  # Da Nang center
        start_lon: float = 108.2022,
    ) -> Dict[str, Any]:
        """
        Create a travel itinerary
        
        Args:
            duration_days: Number of days
            interests: User interests (beach, seafood, culture, etc.)
            budget: Budget level (low, medium, high, luxury)
            family_size: Number of people
            start_lat, start_lon: Starting location
            
        Returns:
            {
                "title": "...",
                "description": "...",
                "stops": [...],
                "summary": "..."
            }
        """
        logger.info(f"Creating {duration_days}-day itinerary for interests: {interests}")
        
        # Step 1: Find candidate places using Graph-RAG
        candidates = []
        for interest in interests[:3]:  # Top 3 interests
            result = await rag_pipeline.find_places_with_context(
                lat=start_lat,
                lon=start_lon,
                user_query=interest,
                radius_km=10.0,
                limit=10,
            )
            candidates.extend(result["places"])
        
        # Remove duplicates
        unique_places = {p["id"]: p for p in candidates}.values()
        places = list(unique_places)[:duration_days * 3]  # ~3 places per day
        
        if not places:
            return {
                "title": "No Itinerary Available",
                "description": "Could not find suitable places for your interests.",
                "stops": [],
                "summary": "Please try different search criteria."
            }
        
        # Step 2: Optimize route using TSP
        place_coords = [(p["id"], start_lat, start_lon) for p in places]
        # Note: This is simplified - should get actual coordinates from places
        
        # Step 3: Generate itinerary with LLM
        places_text = "\n".join([
            f"{i+1}. {p['name']} ({p['category']}) - {p.get('distance_km', 0):.1f}km"
            for i, p in enumerate(places[:10])
        ])
        
        messages = [
            {"role": "system", "content": "You are an expert Da Nang travel planner."},
            {"role": "user", "content": f"Create a {duration_days}-day itinerary for {family_size} people with interests: {', '.join(interests)}. Budget: {budget}.\n\nAvailable places:\n{places_text}\n\nGenerate a brief title and description."}
        ]
        
        llm_response = await llm_client.chat_completion(messages, max_tokens=300)
        
        # Parse LLM response (simplified)
        lines = llm_response.split("\n")
        title = lines[0].replace("Title:", "").strip() if lines else "Your Da Nang Adventure"
        description = "\n".join(lines[1:]).strip() if len(lines) > 1 else "Personalized itinerary for Da Nang"
        
        # Step 4: Create stops
        stops = []
        for i, place in enumerate(places[:duration_days * 3]):
            stops.append({
                "order": i + 1,
                "place_id": place["id"],
                "place_name": place["name"],
                "category": place["category"],
                "description": f"Visit {place['name']} - a popular {place['category']} spot.",
                "duration_minutes": 90,  # Default 1.5h
                "transport_mode": "grab" if i > 0 else None,
                "transport_duration_minutes": 15 if i > 0 else None,
            })
        
        return {
            "title": title,
            "description": description,
            "stops": stops,
            "summary": llm_response,
            "estimated_cost": self._estimate_cost(budget, duration_days, family_size),
        }
    
    def _estimate_cost(self, budget: str, days: int, people: int) -> float:
        """Estimate total cost based on budget level"""
        daily_per_person = {
            "low": 500000,  # 500k VND
            "medium": 1000000,  # 1M VND
            "high": 2000000,  # 2M VND
            "luxury": 5000000,  # 5M VND
        }
        
        return daily_per_person.get(budget, 1000000) * days * people


# Global instance
planner_agent = PlannerAgent()
