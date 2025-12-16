"""
Convert PlaceData JSON to natural language text for embeddings
Multi-strategy: template-based + optional LLM enhancement
"""

from typing import List, Dict
from .models import PlaceData, Review
from .config import TEXT_EMBEDDING_TYPES, USE_LLM_ENHANCEMENT, LLM_MODEL, GOOGLE_API_KEY
import google.generativeai as genai

# Configure Gemini
if USE_LLM_ENHANCEMENT:
    genai.configure(api_key=GOOGLE_API_KEY)


class TextConverter:
    """Convert place data to various text representations"""
    
    @staticmethod
    def to_master_summary(place: PlaceData) -> str:
        """
        Consolidated summary - main embedding type
        Template-based, no LLM
        """
        # Format reviews
        review_highlights = TextConverter._format_top_reviews(place.reviews, max_reviews=3)
        
        text = f"""
{place.name} ({place.category})

📍 Địa chỉ: {place.address}
⭐ Đánh giá: {place.rating}/5 ({place.reviews_count} đánh giá)
💰 Giá: {place.price_range or 'Liên hệ'}
📞 {place.phone or ''}

{place.description}

{f"🌟 Đặc sản: {place.specialty}" if place.specialty else ""}

{review_highlights}
        """.strip()
        
        return text
    
    @staticmethod
    def to_food_focused(place: PlaceData) -> str:
        """Food-specific description for restaurants/cafes"""
        
        # Extract food mentions from reviews
        food_mentions = []
        for review in place.reviews[:5]:
            text_lower = review.text.lower()
            # Look for food-related phrases
            if any(word in text_lower for word in ['ngon', 'tươi', 'thơm', 'vị', 'món']):
                # Extract sentence
                sentences = review.text.split('.')
                for sent in sentences:
                    if any(word in sent.lower() for word in ['ngon', 'tươi', 'thơm']):
                        food_mentions.append(sent.strip())
                        break
        
        text = f"""
{place.name} - {place.category}

Đặc sản: {place.specialty or place.description}

Giá: {place.price_range or 'Liên hệ'}

Nhận xét về món ăn:
{chr(10).join(f"• {mention}" for mention in food_mentions[:4])}
        """.strip()
        
        return text
    
    @staticmethod
    def to_ambiance_description(place: PlaceData) -> str:
        """Vibe, mood, atmosphere description"""
        
        # Extract ambiance keywords from reviews
        vibe_keywords = []
        ambiance_words = [
            'view', 'đẹp', 'yên tĩnh', 'chill', 'sang trọng', 
            'romantic', 'ấm cúng', 'rộng rãi', 'thoáng mát',
            'hiện đại', 'vintage', 'truyền thống', 'cozy'
        ]
        
        for review in place.reviews:
            text_lower = review.text.lower()
            for word in ambiance_words:
                if word in text_lower:
                    vibe_keywords.append(word)
        
        # Deduplicate and join
        unique_vibes = list(set(vibe_keywords))
        
        text = f"""
{place.name} - Không gian và phong cách

Loại hình: {place.category}
Địa điểm: {place.address}

Đặc điểm không gian: {', '.join(unique_vibes[:8]) if unique_vibes else 'Thoải mái, thân thiện'}

{place.description}
        """.strip()
        
        return text
    
    @staticmethod
    def to_practical_info(place: PlaceData) -> str:
        """Practical details: price, location, parking, etc."""
        
        # Extract practical info from reviews
        practical_mentions = []
        practical_keywords = ['parking', 'đỗ xe', 'wifi', 'giao', 'ship', 'mở cửa', 'đông']
        
        for review in place.reviews[:5]:
            text_lower = review.text.lower()
            for keyword in practical_keywords:
                if keyword in text_lower:
                    sentences = review.text.split('.')
                    for sent in sentences:
                        if keyword in sent.lower():
                            practical_mentions.append(sent.strip())
                            break
        
        text = f"""
{place.name} - Thông tin thực tế

Giá: {place.price_range or 'Liên hệ'}
Địa chỉ: {place.address}
Điện thoại: {place.phone or 'Không có'}
Google Maps: {place.google_maps_url}

Tiện ích: {', '.join(place.tags) if place.tags else 'Cơ bản'}

{chr(10).join(f"• {mention}" for mention in practical_mentions[:3])}
        """.strip()
        
        return text
    
    @staticmethod
    def to_reviews_summary(place: PlaceData) -> str:
        """Aggregated positive review highlights"""
        
        # Sort reviews by rating
        sorted_reviews = sorted(place.reviews, key=lambda r: r.rating, reverse=True)
        
        highlights = []
        for review in sorted_reviews[:5]:
            if review.rating >= 4:
                # Take first sentence or first 100 chars
                text = review.text.split('.')[0].strip()
                if len(text) > 150:
                    text = text[:150] + "..."
                highlights.append(f"⭐ {review.rating}/5: {text}")
        
        text = f"""
{place.name} - Điểm nổi bật từ khách hàng

Đánh giá trung bình: {place.rating}/5 ({place.reviews_count} đánh giá)

{chr(10).join(highlights)}
        """.strip()
        
        return text
    
    @staticmethod
    async def to_llm_enhanced(place: PlaceData) -> str:
        """
        LLM-generated enhanced description
        Use for premium/high-rated places only
        """
        if not USE_LLM_ENHANCEMENT:
            return TextConverter.to_master_summary(place)
        
        # Prepare context for LLM
        reviews_text = "\n".join([
            f"- {r.text[:100]}..." 
            for r in place.reviews[:5]
        ])
        
        prompt = f"""
Bạn là travel blogger chuyên nghiệp. Viết mô tả hấp dẫn về địa điểm sau cho du khách.

Tên: {place.name}
Loại: {place.category}
Đánh giá: {place.rating}/5
Giá: {place.price_range}
Mô tả hiện tại: {place.description}
Đặc sản: {place.specialty}

Một số review:
{reviews_text}

YÊU CẦU:
- Độ dài: 150-200 từ
- Tập trung vào điểm nổi bật, độc đáo
- Ngôn ngữ tự nhiên, không formal
- Không lặp lại thông tin đã cho (tên, giá, rating)
- Viết bằng tiếng Việt

CHỈ TRẢ VỀ VĂN BẢN MÔ TẢ, KHÔNG THÊM TIÊU ĐỀ HAY PHẦN GIỚI THIỆU.
        """.strip()
        
        try:
            model = genai.GenerativeModel(LLM_MODEL)
            response = await model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ LLM enhancement failed for {place.id}: {e}")
            # Fallback to template
            return TextConverter.to_master_summary(place)
    
    @staticmethod
    def _format_top_reviews(reviews: List[Review], max_reviews: int = 3) -> str:
        """Format top reviews for display"""
        if not reviews:
            return ""
        
        # Sort by rating
        sorted_reviews = sorted(reviews, key=lambda r: r.rating, reverse=True)
        
        lines = ["Đánh giá nổi bật:"]
        for review in sorted_reviews[:max_reviews]:
            # Truncate long reviews
            text = review.text
            if len(text) > 150:
                text = text[:150] + "..."
            lines.append(f"• ⭐ {review.rating}/5: {text}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_all_texts(place: PlaceData) -> Dict[str, str]:
        """
        Generate all text embedding types for a place
        Returns dict: {embedding_type: text_content}
        """
        texts = {}
        
        # Always generate master
        texts["master"] = TextConverter.to_master_summary(place)
        
        # Category-specific
        for emb_type, config in TEXT_EMBEDDING_TYPES.items():
            if emb_type == "master":
                continue  # Already done
            
            # Check condition
            if "condition" in config:
                if not config["condition"](place.__dict__):
                    continue
            elif not config.get("always_generate", False):
                continue
            
            # Generate text
            if emb_type == "category_food":
                texts[emb_type] = TextConverter.to_food_focused(place)
            elif emb_type == "ambiance":
                texts[emb_type] = TextConverter.to_ambiance_description(place)
            elif emb_type == "practical":
                texts[emb_type] = TextConverter.to_practical_info(place)
            elif emb_type == "reviews_positive":
                texts[emb_type] = TextConverter.to_reviews_summary(place)
            # llm_enhanced handled separately (async)
        
        return texts
