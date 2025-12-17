
import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.mcp.tools import mcp_tools

async def main():
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        print("Error: BRAVE_API_KEY not set")
        return

    print("Testing Social Search Integration...")
    try:
        results = await mcp_tools.search_social_media("AI Trends", limit=3)
        print(f"Found {len(results)} results:")
        for r in results:
            print(f"- [{r.platform}] {r.title} ({r.age})")
            print(f"  Url: {r.url}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
