"""
LocalMate Agent Test Script - Comprehensive Tool Coverage

Tests 5 queries covering ALL tools in both modes:
1. Greeting (no tools) - tests greeting detection
2. Text search (retrieve_context_text)
3. Location search (find_nearby_places)  
4. Social search (search_social_media)
5. Complex query (multiple tools in ReAct mode)

Run: python tests/test_react_comparison.py
"""

import asyncio
import json
import time
from datetime import datetime
import httpx

# =============================================================================
# CONFIGURATION
# =============================================================================

# API Settings - Use localhost for local testing
API_BASE = "http://localhost:8000/api/v1"
USER_ID = "test_comprehensive"

# Delay Settings (in seconds)
SINGLE_MODE_DELAY = 5        # Delay between queries in single mode
REACT_MODE_DELAY = 10        # Delay between queries in ReAct mode
MODE_SWITCH_DELAY = 5        # Delay between switching modes
REQUEST_TIMEOUT = 120        # Timeout for each API request

# Provider settings
PROVIDER = "MegaLLM"
MODEL = "deepseek-ai/deepseek-v3.1-terminus"

# =============================================================================
# 5 TEST CASES - Covering ALL tools
# =============================================================================

TEST_CASES = [
    {
        "id": 1,
        "query": "xin chào",
        "description": "Greeting - No tools expected",
        "expected_tools": [],
        "tool_coverage": "No tools (greeting detection)",
    },
    {
        "id": 2,
        "query": "Quán cafe view đẹp ở Đà Nẵng",
        "description": "Text search - Semantic search in reviews",
        "expected_tools": ["retrieve_context_text"],
        "tool_coverage": "retrieve_context_text",
    },
    {
        "id": 3,
        "query": "Nhà hàng gần Cầu Rồng",
        "description": "Location search - Neo4j spatial query",
        "expected_tools": ["find_nearby_places"],
        "tool_coverage": "find_nearby_places",
    },
    {
        "id": 4,
        "query": "Review quán ăn hot trên tiktok Đà Nẵng",
        "description": "Social search - Brave API news/trends",
        "expected_tools": ["search_social_media"],
        "tool_coverage": "search_social_media",
    },
    {
        "id": 5,
        "query": "Quán cafe không gian đẹp gần biển Mỹ Khê có review tốt",
        "description": "Complex query - Multiple tools (ReAct advantage)",
        "expected_tools": ["find_nearby_places", "retrieve_context_text"],
        "tool_coverage": "Multiple tools",
    },
]


async def run_test(client: httpx.AsyncClient, test_case: dict, react_mode: bool) -> dict:
    """Run a single test case and return results."""
    start_time = time.time()
    
    try:
        response = await client.post(
            f"{API_BASE}/chat",
            json={
                "message": test_case["query"],
                "user_id": USER_ID,
                "provider": PROVIDER,
                "model": MODEL,
                "react_mode": react_mode,
                "max_steps": 5,
            },
            timeout=float(REQUEST_TIMEOUT),
        )
        
        duration = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "test_id": test_case["id"],
                "query": test_case["query"],
                "description": test_case["description"],
                "tool_coverage": test_case["tool_coverage"],
                "expected_tools": test_case["expected_tools"],
                "react_mode": react_mode,
                "response": data.get("response", "")[:300],
                "workflow": data.get("workflow", {}),
                "tools_used": data.get("tools_used", []),
                "places_count": len(data.get("places", [])),
                "api_duration_ms": data.get("duration_ms", 0),
                "total_duration_ms": duration,
            }
        else:
            return {
                "success": False,
                "test_id": test_case["id"],
                "query": test_case["query"],
                "react_mode": react_mode,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "total_duration_ms": duration,
            }
    
    except Exception as e:
        return {
            "success": False,
            "test_id": test_case["id"],
            "query": test_case["query"],
            "react_mode": react_mode,
            "error": str(e),
            "total_duration_ms": (time.time() - start_time) * 1000,
        }


def check_tool_match(expected: list, actual: list) -> str:
    """Check if expected tools match actual tools used."""
    if not expected and not actual:
        return "✅ Match"
    if set(expected) == set(actual):
        return "✅ Match"
    if set(expected).issubset(set(actual)):
        return "⚠️ Extra tools"
    if any(t in actual for t in expected):
        return "⚠️ Partial"
    return "❌ Mismatch"


def generate_report(single_results: list, react_results: list) -> str:
    """Generate detailed markdown report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate stats
    single_success = sum(1 for r in single_results if r.get('success'))
    react_success = sum(1 for r in react_results if r.get('success'))
    single_avg = sum(r.get('api_duration_ms', 0) for r in single_results if r.get('success')) / max(1, single_success)
    react_avg = sum(r.get('api_duration_ms', 0) for r in react_results if r.get('success')) / max(1, react_success)
    
    # Collect all unique tools used
    all_tools_single = set()
    all_tools_react = set()
    for r in single_results:
        if r.get('success'):
            all_tools_single.update(r.get('tools_used', []))
    for r in react_results:
        if r.get('success'):
            all_tools_react.update(r.get('tools_used', []))
    
    report = f"""# LocalMate Agent Comprehensive Test Report

**Generated:** {timestamp}  
**Provider:** {PROVIDER}  
**Model:** {MODEL}

---

## Summary

| Metric | Single Mode | ReAct Mode |
|--------|:-----------:|:----------:|
| Success Rate | {single_success}/{len(single_results)} | {react_success}/{len(react_results)} |
| Avg Duration | {single_avg:.0f}ms | {react_avg:.0f}ms |
| Unique Tools | {len(all_tools_single)} | {len(all_tools_react)} |

### Tools Covered

| Tool | Single Mode | ReAct Mode |
|------|:-----------:|:----------:|
| `retrieve_context_text` | {"✅" if "retrieve_context_text" in all_tools_single else "❌"} | {"✅" if "retrieve_context_text" in all_tools_react else "❌"} |
| `find_nearby_places` | {"✅" if "find_nearby_places" in all_tools_single else "❌"} | {"✅" if "find_nearby_places" in all_tools_react else "❌"} |
| `search_social_media` | {"✅" if "search_social_media" in all_tools_single else "❌"} | {"✅" if "search_social_media" in all_tools_react else "❌"} |
| No tools (greeting) | {"✅" if any(not r.get('tools_used') for r in single_results if r.get('success')) else "❌"} | {"✅" if any(not r.get('tools_used') for r in react_results if r.get('success')) else "❌"} |

---

## Test Results

| ID | Description | Single Tools | ReAct Tools | Match |
|----|-------------|--------------|-------------|-------|
"""
    
    for single, react in zip(single_results, react_results):
        test_id = single.get("test_id", "?")
        desc = single.get("description", "")[:30]
        expected = single.get("expected_tools", [])
        
        if single.get("success"):
            single_tools = ", ".join(single.get("tools_used", [])) or "∅ (none)"
            single_match = check_tool_match(expected, single.get("tools_used", []))
        else:
            single_tools = "❌ Error"
            single_match = "❌"
        
        if react.get("success"):
            react_tools = ", ".join(react.get("tools_used", [])) or "∅ (none)"
            react_match = check_tool_match(expected, react.get("tools_used", []))
        else:
            react_tools = "❌ Error"
            react_match = "❌"
        
        report += f"| {test_id} | {desc} | {single_tools} | {react_tools} | {single_match}/{react_match} |\n"
    
    report += "\n---\n\n## Detailed Results\n\n"
    
    for i, (single, react) in enumerate(zip(single_results, react_results)):
        test_id = single.get("test_id", i + 1)
        query = single.get("query", "N/A")
        description = single.get("description", "")
        coverage = single.get("tool_coverage", "")
        
        report += f"""### Test {test_id}: {description}

**Query:** `{query}`  
**Expected Tools:** {coverage}

| Mode | Status | Duration | Tools Used | Places |
|------|--------|----------|------------|--------|
"""
        
        if single.get("success"):
            s_tools = ", ".join(single.get("tools_used", [])) or "None"
            report += f"| Single | ✅ | {single.get('api_duration_ms', 0):.0f}ms | {s_tools} | {single.get('places_count', 0)} |\n"
        else:
            report += f"| Single | ❌ | - | Error: {single.get('error', 'Unknown')[:50]} | - |\n"
        
        if react.get("success"):
            r_tools = ", ".join(react.get("tools_used", [])) or "None"
            report += f"| ReAct | ✅ | {react.get('api_duration_ms', 0):.0f}ms | {r_tools} | {react.get('places_count', 0)} |\n"
        else:
            report += f"| ReAct | ❌ | - | Error: {react.get('error', 'Unknown')[:50]} | - |\n"
        
        report += "\n"
        
        # Show response preview for successful tests
        if single.get("success"):
            report += f"**Single Response:** {single.get('response', '')[:150]}...\n\n"
        if react.get("success"):
            report += f"**ReAct Response:** {react.get('response', '')[:150]}...\n\n"
        
        report += "---\n\n"
    
    # Overall verdict
    all_tools_expected = {"retrieve_context_text", "find_nearby_places", "search_social_media"}
    single_coverage = all_tools_expected.issubset(all_tools_single)
    react_coverage = all_tools_expected.issubset(all_tools_react)
    
    report += f"""## Verdict

| Criteria | Single Mode | ReAct Mode |
|----------|:-----------:|:----------:|
| All tests passed | {"✅" if single_success == len(single_results) else "❌"} | {"✅" if react_success == len(react_results) else "❌"} |
| All 3 search tools covered | {"✅" if single_coverage else "❌"} | {"✅" if react_coverage else "❌"} |
| Greeting detection works | {"✅" if any(not r.get('tools_used') and r.get('success') for r in single_results) else "❌"} | {"✅" if any(not r.get('tools_used') and r.get('success') for r in react_results) else "❌"} |

**Overall:** {"🎉 ALL TESTS PASSED!" if single_success == len(single_results) and react_success == len(react_results) else "⚠️ Some tests failed"}
"""
    
    return report


async def main():
    """Main test runner."""
    print("=" * 60)
    print("LocalMate Agent Comprehensive Test")
    print(f"Provider: {PROVIDER} | Model: {MODEL}")
    print("=" * 60)
    print()
    
    single_results = []
    react_results = []
    
    async with httpx.AsyncClient() as client:
        # Test Single Mode (react_mode=False)
        print(f"📌 Running Single Mode Tests (react_mode=false, {SINGLE_MODE_DELAY}s delay)...")
        print("-" * 50)
        
        for i, test in enumerate(TEST_CASES):
            print(f"  [{test['id']}/5] {test['description'][:40]}...")
            result = await run_test(client, test, react_mode=False)
            single_results.append(result)
            
            status = "✅" if result.get("success") else "❌"
            tools = ", ".join(result.get("tools_used", [])) or "None"
            places = result.get("places_count", 0)
            print(f"       {status} Tools: [{tools}] | Places: {places} | {result.get('api_duration_ms', 0):.0f}ms")
            
            if i < len(TEST_CASES) - 1:
                await asyncio.sleep(SINGLE_MODE_DELAY)
        
        print()
        print(f"⏸️  Waiting {MODE_SWITCH_DELAY}s before ReAct mode...")
        await asyncio.sleep(MODE_SWITCH_DELAY)
        
        # Test ReAct Mode (react_mode=True)
        print()
        print(f"🧠 Running ReAct Mode Tests (react_mode=true, {REACT_MODE_DELAY}s delay)...")
        print("-" * 50)
        
        for i, test in enumerate(TEST_CASES):
            print(f"  [{test['id']}/5] {test['description'][:40]}...")
            result = await run_test(client, test, react_mode=True)
            react_results.append(result)
            
            status = "✅" if result.get("success") else "❌"
            tools = ", ".join(result.get("tools_used", [])) or "None"
            places = result.get("places_count", 0)
            steps = len(result.get("workflow", {}).get("steps", []))
            print(f"       {status} Tools: [{tools}] | Places: {places} | Steps: {steps} | {result.get('api_duration_ms', 0):.0f}ms")
            
            if i < len(TEST_CASES) - 1:
                await asyncio.sleep(REACT_MODE_DELAY)
    
    # Generate report
    print()
    print("📝 Generating report...")
    report = generate_report(single_results, react_results)
    
    # Save report
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, "react_comparison_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Report saved to: {report_path}")
    print()
    
    # Quick summary
    single_success = sum(1 for r in single_results if r.get('success'))
    react_success = sum(1 for r in react_results if r.get('success'))
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Single Mode: {single_success}/{len(single_results)} passed")
    print(f"ReAct Mode:  {react_success}/{len(react_results)} passed")
    print()
    
    if single_success == len(single_results) and react_success == len(react_results):
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ Some tests failed - check report for details")


if __name__ == "__main__":
    asyncio.run(main())
