"""
Guide Agent

Generate Guide Pack for Grab drivers với local tips và stories
"""

from typing import List, Dict, Any
from app.shared.graph.rag_pipeline import rag_pipeline
from app.shared.integrations.llm_client import llm_client
from app.shared.utils.language_utils import get_greeting, SUPPORTED_LANGUAGES
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class GuideAgent:
    """AI Guide Pack Generator for Drivers"""
    
    async def generate_guide_pack(
        self,
        place_id: int,
        place_name: str,
        latitude: float,
        longitude: float,
        passenger_language: str = "en",
        include_fun_facts: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate guide pack for a specific location
        
        Args:
            place_id: Current place ID
            place_name: Place name
            latitude, longitude: Current location
            passenger_language: Passenger's preferred language
            include_fun_facts: Include fun facts card
            
        Returns:
            {
                "cards": [...],
                "driver_summary": "...",
                "quick_phrases": [...]
            }
        """
        logger.info(f"Generating guide pack for {place_name}")
        
        cards = []
        
        # Card 1: Place Information
        place_card = await self._generate_place_card(place_name, latitude, longitude)
        cards.append(place_card)
        
        # Card 2: Fun Facts (if requested)
        if include_fun_facts:
            fun_fact_card = await self._generate_fun_fact_card(place_name)
            cards.append(fun_fact_card)
        
        # Card 3: Local Tips
        local_tip_card = await self._generate_local_tip_card(place_name, passenger_language)
        cards.append(local_tip_card)
        
        # Generate quick phrases
        quick_phrases = self._generate_language_cards(passenger_language)
        
        # Generate driver summary
        driver_summary = await self._generate_driver_summary(place_name, passenger_language)
        
        return {
            "cards": cards,
            "driver_summary": driver_summary,
            "quick_phrases": quick_phrases,
        }
    
    async def _generate_place_card(self, place_name: str, lat: float, lon: float) -> Dict[str, Any]:
        """Generate place information card"""
        # Get nearby context using Graph-RAG
        context = await rag_pipeline.find_places_with_context(
            lat=lat,
            lon=lon,
            user_query=f"information about {place_name}",
            limit=5,
        )
        
        return {
            "card_type": "place_info",
            "title": place_name,
            "content": context.get("summary", f"A popular destination in Da Nang near {place_name}."),
            "place_name": place_name,
        }
    
    async def _generate_fun_fact_card(self, place_name: str) -> Dict[str, Any]:
        """Generate fun fact card using LLM"""
        messages = [
            {"role": "system", "content": "You are a Da Nang local guide. Generate ONE interesting, brief fun fact."},
            {"role": "user", "content": f"Generate a fun fact about {place_name} in Da Nang. Keep it to 2-3 sentences."}
        ]
        
        fun_fact = await llm_client.chat_completion(messages, max_tokens=100)
        
        return {
            "card_type": "fun_fact",
            "title": f"Fun Fact: {place_name}",
            "content": fun_fact,
        }
    
    async def _generate_local_tip_card(self, place_name: str, language: str) -> Dict[str, Any]:
        """Generate local tip card"""
        messages = [
            {"role": "system", "content": "You are a Grab driver in Da Nang. Give practical local tips."},
            {"role": "user", "content": f"Give a brief local tip about {place_name} that would help a {language}-speaking tourist. 2-3 sentences."}
        ]
        
        tip = await llm_client.chat_completion(messages, max_tokens=100)
        
        return {
            "card_type": "local_tip",
            "title": "Local Tip",
            "content": tip,
        }
    
    def _generate_language_cards(self, passenger_language: str) -> List[Dict[str, Any]]:
        """Generate quick phrase cards"""
        common_phrases = [
            {
                "english": "Welcome to Da Nang!",
                "vietnamese": "Chào mừng đến Đà Nẵng!",
                "japanese": "ダナンへようこそ!",
                "korean": "다낭에 오신 것을 환영합니다!",
                "chinese": "欢迎来到岘港!",
            },
            {
                "english": "This is a famous place",
                "vietnamese": "Đây là một địa điểm nổi tiếng",
                "japanese": "ここは有名な場所です",
                "korean": "이곳은 유명한 장소입니다",
                "chinese": "这是一个著名的地方",
            },
            {
                "english": "Enjoy your visit!",
                "vietnamese": "Chúc bạn tham quan vui vẻ!",
                "japanese": "楽しんでください!",
                "korean": "즐거운 시간 보내세요!",
                "chinese": "祝您旅途愉快!",
            },
        ]
        
        return common_phrases
    
    async def _generate_driver_summary(self, place_name: str, language: str) -> str:
        """Generate brief summary for driver"""
        return f"Guide Pack for {place_name}. Passenger language: {language}. Use the cards below to provide interesting information and engage with your passenger!"


# Global instance
guide_agent = GuideAgent()
