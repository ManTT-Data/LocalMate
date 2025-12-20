"""Smart Plan Service - Generate optimized, enriched travel plans.

Uses Social Media Tool for research and LLM for intelligent scheduling.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field

from app.mcp.tools.social_tool import search_social_media, SocialSearchResult
from app.shared.integrations.gemini_client import GeminiClient
from app.shared.prompts import SMART_PLAN_SYSTEM_PROMPT, build_smart_plan_prompt
from app.planner.tsp import optimize_route, haversine


@dataclass
class PlaceDetail:
    """Rich detail for a place in smart plan."""
    place_id: str
    name: str
    category: str = ""
    lat: float = 0.0
    lng: float = 0.0
    recommended_time: str = ""           # "21:00"
    suggested_duration_min: int = 60     # Default 1 hour
    tips: list[str] = field(default_factory=list)
    highlights: str = ""                  # Summary from research
    social_mentions: list[str] = field(default_factory=list)
    order: int = 0


@dataclass
class DayPlan:
    """Single day plan."""
    day_index: int
    date: date | None = None
    places: list[PlaceDetail] = field(default_factory=list)
    day_summary: str = ""
    day_distance_km: float = 0.0


@dataclass 
class SmartPlan:
    """Complete optimized plan with enriched details."""
    itinerary_id: str
    title: str
    total_days: int
    days: list[DayPlan]
    summary: str = ""
    total_distance_km: float = 0.0
    estimated_total_duration_min: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


class SmartPlanService:
    """Service for generating smart, enriched travel plans."""
    
    # Da Nang local knowledge - special timing for attractions
    DANANG_TIMING_HINTS = {
        "cầu rồng": {"time": "21:00", "tip": "Xem cầu rồng phun lửa/nước (T7, CN)"},
        "dragon bridge": {"time": "21:00", "tip": "Fire/water show (Sat, Sun)"},
        "cầu tình yêu": {"time": "19:00", "tip": "Đẹp nhất khi lên đèn"},
        "bà nà hills": {"time": "08:00", "tip": "Đến sớm tránh đông, mát mẻ"},
        "bãi biển mỹ khê": {"time": "05:30", "tip": "Ngắm bình minh tuyệt đẹp"},
        "my khe beach": {"time": "05:30", "tip": "Beautiful sunrise"},
        "chợ hàn": {"time": "07:00", "tip": "Sáng sớm đồ tươi, giá tốt"},
        "chợ cồn": {"time": "06:00", "tip": "Chợ lớn nhất, đi sớm"},
        "sơn trà": {"time": "05:00", "tip": "Săn mây, ngắm voọc"},
        "ngũ hành sơn": {"time": "07:00", "tip": "Mát mẻ, ít đông"},
        "hội an": {"time": "16:00", "tip": "Chiều tối đẹp nhất, thả đèn hoa đăng"},
    }
    
    # Default category timings
    CATEGORY_TIMING = {
        "cafe": {"time": "09:00", "duration": 60},
        "restaurant": {"time": "12:00", "duration": 90},
        "beach": {"time": "06:00", "duration": 120},
        "attraction": {"time": "09:00", "duration": 90},
        "shopping": {"time": "10:00", "duration": 60},
        "nightlife": {"time": "20:00", "duration": 120},
    }
    
    def __init__(self, model: str = "gemini-3-flash-preview"):
        """Initialize with Gemini model."""
        self.llm = GeminiClient(model=model)
    
    async def research_places(
        self, 
        place_names: list[str],
        freshness: str = "pw"
    ) -> dict[str, list[SocialSearchResult]]:
        """
        Use Social Tool to gather info about each place.
        
        Args:
            place_names: List of place names to research
            freshness: Brave Search freshness param (pw=past week)
            
        Returns:
            Dict mapping place_name to list of social results
        """
        research = {}
        
        # Parallel research for all places
        async def research_one(name: str):
            query = f"{name} Đà Nẵng review"
            results = await search_social_media(
                query=query,
                limit=5,
                freshness=freshness
            )
            return name, results
        
        tasks = [research_one(name) for name in place_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple):
                name, social_results = result
                research[name] = social_results
            else:
                # Exception occurred, skip
                pass
                
        return research
    
    def _get_timing_hint(self, place_name: str, category: str) -> tuple[str, str]:
        """Get recommended time and tip for a place."""
        name_lower = place_name.lower()
        
        # Check specific place hints first
        for keyword, hints in self.DANANG_TIMING_HINTS.items():
            if keyword in name_lower:
                return hints["time"], hints["tip"]
        
        # Fall back to category timing
        cat_lower = category.lower() if category else ""
        for cat_key, timing in self.CATEGORY_TIMING.items():
            if cat_key in cat_lower:
                return timing["time"], ""
        
        # Default
        return "10:00", ""
    
    def _format_social_mentions(self, results: list[SocialSearchResult]) -> list[str]:
        """Format social results as readable mentions."""
        mentions = []
        for r in results[:3]:  # Top 3
            platform = r.platform if r.platform != "Web" else ""
            if platform:
                mentions.append(f"[{platform}] {r.title[:80]}...")
            else:
                mentions.append(r.title[:80])
        return mentions
    
    async def generate_smart_plan(
        self,
        places: list[dict],  # List of {place_id, name, category, lat, lng, ...}
        title: str = "My Trip",
        itinerary_id: str = "",
        total_days: int = 1,
        start_date: date | None = None,
        include_social_research: bool = True,
        freshness: str = "pw"
    ) -> SmartPlan:
        """
        Generate optimized smart plan with enriched details.
        
        Args:
            places: List of places with basic info
            title: Plan title
            itinerary_id: Reference ID
            total_days: Number of days
            start_date: Optional start date
            include_social_research: Whether to search social media
            freshness: Social search freshness
            
        Returns:
            SmartPlan with optimized timing and enriched details
        """
        start_time = time.time()
        
        # Step 1: Research places (if enabled)
        research = {}
        if include_social_research:
            place_names = [p.get("name", "") for p in places if p.get("name")]
            research = await self.research_places(place_names, freshness)
        
        # Step 2: Get timing hints and build place details
        place_details = []
        for i, place in enumerate(places):
            name = place.get("name", f"Place {i+1}")
            category = place.get("category", "")
            
            rec_time, tip = self._get_timing_hint(name, category)
            
            # Get social mentions
            social_results = research.get(name, [])
            social_mentions = self._format_social_mentions(social_results)
            
            # Build highlights from social research
            highlights = ""
            if social_results:
                descriptions = [r.description for r in social_results[:2] if r.description]
                if descriptions:
                    highlights = " ".join(descriptions)[:300]
            
            tips = [tip] if tip else []
            
            detail = PlaceDetail(
                place_id=place.get("place_id", ""),
                name=name,
                category=category,
                lat=place.get("lat", 0.0),
                lng=place.get("lng", 0.0),
                recommended_time=rec_time,
                suggested_duration_min=self.CATEGORY_TIMING.get(category.lower(), {}).get("duration", 60),
                tips=tips,
                highlights=highlights,
                social_mentions=social_mentions,
                order=i + 1
            )
            place_details.append(detail)
        
        # Step 3: Use LLM to optimize and enhance
        enhanced_plan = await self._llm_enhance_plan(
            place_details=place_details,
            total_days=total_days,
            research=research
        )
        
        # Step 4: Organize into days
        days = self._organize_into_days(
            place_details=enhanced_plan if enhanced_plan else place_details,
            total_days=total_days,
            start_date=start_date
        )
        
        # Step 5: Calculate distances
        total_distance = 0.0
        for day in days:
            day.day_distance_km = self._calculate_day_distance(day.places)
            total_distance += day.day_distance_km
        
        # Step 6: Build summary
        summary = await self._generate_summary(title, days, research)
        
        generation_time = (time.time() - start_time) * 1000
        
        return SmartPlan(
            itinerary_id=itinerary_id,
            title=title,
            total_days=total_days,
            days=days,
            summary=summary,
            total_distance_km=round(total_distance, 2),
            estimated_total_duration_min=sum(p.suggested_duration_min for d in days for p in d.places),
            generated_at=datetime.now()
        )
    
    async def _llm_enhance_plan(
        self,
        place_details: list[PlaceDetail],
        total_days: int,
        research: dict
    ) -> list[PlaceDetail] | None:
        """Use LLM to enhance timing and tips."""
        try:
            # Build context for LLM
            places_info = []
            for p in place_details:
                info = {
                    "name": p.name,
                    "category": p.category,
                    "current_time": p.recommended_time,
                    "social_info": p.highlights[:200] if p.highlights else ""
                }
                places_info.append(info)
            
            prompt = build_smart_plan_prompt(places_info, total_days)
            
            response = await self.llm.generate(
                prompt=prompt,
                system_instruction=SMART_PLAN_SYSTEM_PROMPT,
                temperature=0.7
            )
            
            # Parse LLM response and update place details
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                llm_result = json.loads(json_match.group())
                
                # Update place details with LLM suggestions
                if "places" in llm_result:
                    for llm_place in llm_result["places"]:
                        for p in place_details:
                            if p.name.lower() == llm_place.get("name", "").lower():
                                if "time" in llm_place:
                                    p.recommended_time = llm_place["time"]
                                if "tips" in llm_place:
                                    p.tips = llm_place["tips"]
                                if "duration" in llm_place:
                                    p.suggested_duration_min = llm_place["duration"]
                                break
            
            return place_details
            
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return None
    
    def _organize_into_days(
        self,
        place_details: list[PlaceDetail],
        total_days: int,
        start_date: date | None
    ) -> list[DayPlan]:
        """Organize places into days based on timing."""
        if total_days <= 0:
            total_days = 1
            
        # Sort by recommended time
        sorted_places = sorted(place_details, key=lambda p: p.recommended_time)
        
        # Distribute across days
        places_per_day = max(1, len(sorted_places) // total_days)
        
        days = []
        for day_idx in range(total_days):
            start_idx = day_idx * places_per_day
            end_idx = start_idx + places_per_day if day_idx < total_days - 1 else len(sorted_places)
            
            day_places = sorted_places[start_idx:end_idx]
            
            # Sort day places by time
            day_places = sorted(day_places, key=lambda p: p.recommended_time)
            
            # Update order within day
            for i, p in enumerate(day_places):
                p.order = i + 1
            
            day_date = None
            if start_date:
                day_date = start_date + timedelta(days=day_idx)
            
            day = DayPlan(
                day_index=day_idx + 1,
                date=day_date,
                places=day_places,
                day_summary=f"Ngày {day_idx + 1}: {len(day_places)} địa điểm"
            )
            days.append(day)
        
        return days
    
    def _calculate_day_distance(self, places: list[PlaceDetail]) -> float:
        """Calculate total distance for a day's route."""
        if len(places) < 2:
            return 0.0
            
        total = 0.0
        for i in range(len(places) - 1):
            p1, p2 = places[i], places[i + 1]
            if p1.lat and p1.lng and p2.lat and p2.lng:
                total += haversine(p1.lat, p1.lng, p2.lat, p2.lng)
        
        return round(total, 2)
    
    async def _generate_summary(
        self,
        title: str,
        days: list[DayPlan],
        research: dict
    ) -> str:
        """Generate a brief summary of the plan."""
        total_places = sum(len(d.places) for d in days)
        
        # Get highlights from research
        highlights = []
        for results in research.values():
            for r in results[:1]:
                if r.description:
                    highlights.append(r.description[:100])
        
        summary = f"Lịch trình {title} với {total_places} địa điểm trong {len(days)} ngày."
        
        if highlights:
            summary += f" Điểm nhấn: {'; '.join(highlights[:2])}"
        
        return summary


# Global service instance
smart_plan_service = SmartPlanService()
