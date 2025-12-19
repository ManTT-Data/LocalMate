
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
            
    async def search(self, query: str, limit: int = 10, freshness: str = "pw", platforms: List[str] = None) -> List[SocialSearchResult]:
        if not self.api_key:
            print("Warning: BRAVE_API_KEY not found.")
            return []

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        # Default social sites if none provided
        if not platforms:
            # Use general search with social/news filter - don't add complex site: operators
            # as they can cause issues with Brave API for non-English queries
            full_query = f"{query} review tin tức"  # Add context for social/news
        else:
            # Add platform names as context keywords instead of site: operators
            platform_keywords = []
            for p in platforms:
                p = p.lower()
                if "facebook" in p: platform_keywords.append("facebook")
                elif "reddit" in p: platform_keywords.append("reddit")
                elif "twitter" in p or "x" == p: platform_keywords.append("twitter")
                elif "linkedin" in p: platform_keywords.append("linkedin")
                elif "tiktok" in p: platform_keywords.append("tiktok")
                elif "instagram" in p: platform_keywords.append("instagram")
                elif "youtube" in p: platform_keywords.append("youtube")
            
            if platform_keywords:
                full_query = f"{query} {' '.join(platform_keywords)}"
            else:
                full_query = query
            
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
                            # Simple heuristic
                            domain = item.get("url", "").split("//")[-1].split("/")[0]
                            if "reddit" in domain: platform = "Reddit"
                            elif "twitter" in domain or "x.com" in domain: platform = "X (Twitter)"
                            elif "facebook" in domain: platform = "Facebook"
                            
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

# Singleton instance
social_search_tool = BraveSocialSearch()

async def search_social_media(query: str, limit: int = 10, freshness: str = "pw", platforms: List[str] = None) -> List[SocialSearchResult]:
    """
    Search for social media content (news, discussions) about a topic.
    """
    return await social_search_tool.search(query, limit, freshness, platforms)

