import os
import httpx
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class SocialSearchResult:
    title: str
    url: str
    description: str
    age: str = ""
    platform: str = "Web"

# Da Nang & Vietnam Travel Keywords
DANANG_KEYWORDS = {
    'beaches': ['mỹ khê', 'my khe', 'non nuoc', 'bai bien'],
    'attractions': ['bà nà', 'ba na', 'bana hills', 'cầu vàng', 'golden bridge', 
                    'hội an', 'hoi an', 'marble mountains', 'ngũ hành sơn'],
    'food': ['mì quảng', 'mi quang', 'bún chả cá', 'banh xeo', 'cao lầu'],
    'activities': ['surfing', 'diving', 'lặn', 'du lịch'],
}

VIETNAM_HASHTAGS = {
    'general': ['#vietnam', '#vietnamtravel', '#travelvietnam', '#explorevietnam'],
    'danang': ['#danang', '#danangcity', '#danangtravel', '#traveldanang', '#danangtrip'],
    'attractions': ['#banahills', '#hoian', '#halongbay', '#hanoi', '#saigon'],
    'travel': ['#travel', '#wanderlust', '#traveltiktok', '#adventure', '#explore'],
}

TIKTOK_TRAVEL_HASHTAGS = [
    '#traveltiktok', '#travelgram', '#instatravel', '#bucketlist',
    '#vietnamtravel', '#southeastasia', '#travel', '#adventure'
]

def enhance_travel_query(
    query: str, 
    location: str = "danang",
    platform: str = None,
    enhance: bool = True
) -> str:
    """
    Enhance query với travel-specific keywords và hashtags.
    
    Args:
        query: Original search query
        location: Primary location (danang, vietnam, hoian)
        platform: Target platform (tiktok, instagram, etc.)
        enhance: Enable/disable auto-enhancement
    
    Returns:
        Enhanced query string
    """
    if not enhance:
        return query
    
    enhanced = query
    query_lower = query.lower()
    
    # Detect location context
    is_danang = any(loc in query_lower for loc in ['đà nẵng', 'da nang', 'danang'])
    is_vietnam = any(loc in query_lower for loc in ['vietnam', 'việt nam', 'viet nam'])
    
    # Add location if not present and location parameter provided
    if location == "danang" and not (is_danang or is_vietnam):
        enhanced = f"{enhanced} Da Nang"
    
    # Platform-specific enhancements
    if platform and 'tiktok' in platform.lower():
        # Only add #danang hashtag if it's Da Nang context and not already present
        if (is_danang or location == "danang") and '#danang' not in query_lower:
            enhanced = f"{enhanced} #danang"
    
    return enhanced
    
class BraveSocialSearch:
    """
    Native Python implementation of Brave Social Search.
    Wraps Brave Search API with social media specific filters.
    """
    
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            # Fallback or warning? For now assume it will be provided or env
            pass
            
    async def search(
        self, 
        query: str, 
        limit: int = 10, 
        freshness: str = None, 
        platforms: List[str] = None,
        enhance: bool = True,
        location: str = "danang"
    ) -> List[SocialSearchResult]:
        if not self.api_key:
            print("Warning: BRAVE_API_KEY not found.")
            return []

        # Enhancement for travel content
        primary_platform = platforms[0] if platforms else None
        enhanced_query = enhance_travel_query(
            query, 
            location=location,
            platform=primary_platform,
            enhance=enhance
        )
        
        # Platform-specific freshness defaults
        if freshness is None:
            if platforms and any('tiktok' in p.lower() for p in platforms):
                freshness = "pm"  # Past month for TikTok (trending)
            else:
                freshness = "pw"  # Past week for others

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        # Default social sites if none provided
        if not platforms:
            social_sites = [
                'site:twitter.com', 'site:x.com', 
                'site:facebook.com', 
                'site:reddit.com', 
                'site:linkedin.com', 
                'site:tiktok.com',
                'site:instagram.com',
                'site:threads.net'
            ]
        else:
            social_sites = []
            for p in platforms:
                p = p.lower()
                if "facebook" in p: social_sites.append("site:facebook.com")
                elif "reddit" in p: social_sites.append("site:reddit.com")
                elif "twitter" in p or "x" == p: social_sites.extend(["site:twitter.com", "site:x.com"])
                elif "linkedin" in p: social_sites.append("site:linkedin.com")
                elif "tiktok" in p: social_sites.append("site:tiktok.com")
                elif "instagram" in p: social_sites.append("site:instagram.com")
                elif "site:" in p: social_sites.append(p) # Direct operator
        
        # Construct query with site OR operator
        if len(social_sites) > 1:
            sites_query = " OR ".join(social_sites)
            full_query = f"{enhanced_query} ({sites_query})"
        elif len(social_sites) == 1:
            full_query = f"{enhanced_query} {social_sites[0]}"
        else:
            full_query = enhanced_query
            
        params = {
            "q": full_query,
            "count": min(limit, 20),
            "freshness": freshness, 
            "result_filter": "web,news,discussions",
            "text_decorations": 0,
            "spellcheck": 1
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.BASE_URL, 
                    headers=headers, 
                    params=params, 
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                
                # Parse 'web' results (most common)
                if "web" in data and "results" in data["web"]:
                    for item in data["web"]["results"]:
                        # Extract platform from profile or url
                        platform = "Web"
                        if "profile" in item and "name" in item["profile"]:
                            platform = item["profile"]["name"]
                        else:
                            # Enhanced platform detection
                            domain = item.get("url", "").split("//")[-1].split("/")[0]
                            if "reddit" in domain: platform = "Reddit"
                            elif "twitter" in domain or "x.com" in domain: platform = "X (Twitter)"
                            elif "facebook" in domain: platform = "Facebook"
                            elif "tiktok" in domain: platform = "TikTok"
                            elif "instagram" in domain: platform = "Instagram"
                            elif "linkedin" in domain: platform = "LinkedIn"
                            
                        results.append(SocialSearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            description=item.get("description", ""),
                            age=item.get("age", ""),
                            platform=platform
                        ))
                        
                return results
                
            except Exception as e:
                print(f"Error calling Brave Search API: {e}")
                return []

# Tool definition for agent
TOOL_DEFINITION = {
    "name": "search_social_media",
    "description": """Tìm kiếm nội dung mạng xã hội về địa điểm, du lịch Đà Nẵng/Vietnam.

ĐẶC BIỆT TỐI ƯU CHO TIKTOK - nền tảng #1 cho travel content!

Dùng khi:
- Tìm trending videos, viral content về Đà Nẵng
- Xem review, tips, tricks từ du khách thực tế
- Khám phá hidden gems, fun facts về địa điểm
- Thu thập ý kiến cộng đồng về nhà hàng, khách sạn
- Tìm kiếm trải nghiệm và hành trình du lịch

Tính năng thông minh:
- Tự động thêm hashtag #danang
- Query enhancement cho travel content
- Platform-specific optimization (TikTok, Instagram)
- Adaptive freshness (trending vs. comprehensive)

Nền tảng hỗ trợ: 
- TikTok 🔥 (Ưu tiên cho travel content)
- Instagram 📸
- X (Twitter), Facebook, Reddit, LinkedIn, Threads

Tips:
- Để platforms=["tiktok"] cho trending visual content
- Để platforms=None để tìm trên tất cả nền tảng
- Set enhance=False nếu muốn query chính xác (không auto-thêm hashtags)""",
    "parameters": {
        "query": "Query tìm kiếm (VD: 'best beaches', 'quán ăn ngon')",
        "limit": "Số kết quả (mặc định 10, tối đa 20)",
        "freshness": "Độ mới: None (auto), 'pw' (week), 'pm' (month), 'py' (year)",
        "platforms": "Platforms: ['tiktok'], ['instagram'], hoặc None (all)",
        "enhance": "Auto-enhance query (default True)",
        "location": "Location context: 'danang', 'hoian', 'vietnam' (default 'danang')",
    },
}


# Singleton instance
social_search_tool = BraveSocialSearch()

async def search_social_media(
    query: str, 
    limit: int = 10, 
    freshness: str = None,
    platforms: List[str] = None,
    enhance: bool = True,
    location: str = "danang"
) -> List[SocialSearchResult]:
    """
    Search for social media content (news, discussions) with travel optimization.
    """
    return await social_search_tool.search(
        query, limit, freshness, platforms, enhance, location
    )