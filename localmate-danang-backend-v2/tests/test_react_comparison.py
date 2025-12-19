"""
LocalMate Agent Test Script - Single vs ReAct Mode Comparison

Tests 10 queries in both modes:
- Single mode: configurable delay between queries
- ReAct mode: configurable delay between queries  
- Configurable delay between modes

Generates detailed report with all step inputs/outputs.
"""

import asyncio
import json
import time
from datetime import datetime
import httpx

# =============================================================================
# CONFIGURATION - Adjust these values as needed
# =============================================================================

# API Settings
API_BASE = "https://cuong2004-localmate.hf.space/api/v1"
USER_ID = "test_comparison"

# Delay Settings (in seconds)
SINGLE_MODE_DELAY = 10       # Delay between queries in single mode
REACT_MODE_DELAY = 60       # Delay between queries in ReAct mode
MODE_SWITCH_DELAY = 60      # Delay between switching modes
REQUEST_TIMEOUT = 120       # Timeout for each API request

# =============================================================================

# Test Cases - 10 queries covering different scenarios
TEST_CASES = [
    # {
    #     "id": 1,
    #     "query": "Quán cafe view đẹp",
    #     "description": "Simple text search - no location",
    #     "expected_tools": ["retrieve_context_text"],
    # },
    {
        "id": 2,
        "query": "Nhà hàng gần bãi biển Mỹ Khê",
        "description": "Location-based search",
        "expected_tools": ["find_nearby_places"],
    },
    # {
    #     "id": 3,
    #     "query": "Quán cafe có không gian xanh mát gần Cầu Rồng",
    #     "description": "Complex: location + feature (should use multiple tools in ReAct)",
    #     "expected_tools": ["find_nearby_places", "retrieve_context_text"],
    # },
    # {
    #     "id": 4,
    #     "query": "Phở ngon giá rẻ",
    #     "description": "Food-specific text search",
    #     "expected_tools": ["retrieve_context_text"],
    # },
    # {
    #     "id": 5,
    #     "query": "Địa điểm checkin đẹp gần Bà Nà",
    #     "description": "Location + activity type",
    #     "expected_tools": ["find_nearby_places"],
    # },
    # {
    #     "id": 6,
    #     "query": "Quán ăn hải sản có view sông gần trung tâm",
    #     "description": "Complex: location + category + feature",
    #     "expected_tools": ["find_nearby_places", "retrieve_context_text"],
    # },
    # {
    #     "id": 7,
    #     "query": "Khách sạn 5 sao gần biển",
    #     "description": "Hotel + location search",
    #     "expected_tools": ["find_nearby_places"],
    # },
    # {
    #     "id": 8,
    #     "query": "Quán bar có view đẹp về đêm",
    #     "description": "Nightlife text search",
    #     "expected_tools": ["retrieve_context_text"],
    # },
    # {
    #     "id": 9,
    #     "query": "Cafe rooftop gần Sơn Trà có coffee ngon",
    #     "description": "Complex: location + feature + quality",
    #     "expected_tools": ["find_nearby_places", "retrieve_context_text"],
    # },
    # {
    #     "id": 10,
    #     "query": "Nhà hàng Việt Nam authentic gần Rex Hotel",
    #     "description": "Specific location + category + style",
    #     "expected_tools": ["find_nearby_places", "retrieve_context_text"],
    # },
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
                "provider": "MegaLLM",
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
                "react_mode": react_mode,
                "response": data.get("response", "")[:300],
                "workflow": data.get("workflow", {}),
                "tools_used": data.get("tools_used", []),
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


def format_workflow_steps(workflow: dict) -> str:
    """Format workflow steps for report."""
    steps = workflow.get("steps", [])
    if not steps:
        return "No steps recorded"
    
    lines = []
    for step in steps:
        tool = step.get("tool", "N/A")
        purpose = step.get("purpose", "")
        results = step.get("results", 0)
        lines.append(f"  - {step.get('step', 'Unknown')}")
        lines.append(f"    Tool: `{tool}` | Results: {results}")
    
    return "\n".join(lines)


def generate_report(single_results: list, react_results: list) -> str:
    """Generate detailed markdown report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# LocalMate Agent Test Report

**Generated:** {timestamp}

## Summary

| Metric | Single Mode | ReAct Mode |
|--------|-------------|------------|
| Total Tests | {len(single_results)} | {len(react_results)} |
| Success | {sum(1 for r in single_results if r.get('success'))} | {sum(1 for r in react_results if r.get('success'))} |
| Avg Duration | {sum(r.get('api_duration_ms', 0) for r in single_results if r.get('success')) / max(1, sum(1 for r in single_results if r.get('success'))):.0f}ms | {sum(r.get('api_duration_ms', 0) for r in react_results if r.get('success')) / max(1, sum(1 for r in react_results if r.get('success'))):.0f}ms |

---

## Detailed Results

"""
    
    for i, (single, react) in enumerate(zip(single_results, react_results)):
        test_id = single.get("test_id", i + 1)
        query = single.get("query", "N/A")
        description = single.get("description", "")
        
        report += f"""### Test Case {test_id}: {description}

**Query:** `{query}`

#### Single Mode

"""
        if single.get("success"):
            report += f"""- **Status:** ✅ Success
- **Duration:** {single.get('api_duration_ms', 0):.0f}ms
- **Tools Used:** {', '.join(single.get('tools_used', [])) or 'None'}

**Workflow:**
{format_workflow_steps(single.get('workflow', {}))}

**Response Preview:**
> {single.get('response', 'N/A')[:200]}...

"""
        else:
            report += f"""- **Status:** ❌ Failed
- **Error:** {single.get('error', 'Unknown')}

"""
        
        report += """#### ReAct Mode

"""
        if react.get("success"):
            workflow = react.get("workflow", {})
            report += f"""- **Status:** ✅ Success
- **Duration:** {react.get('api_duration_ms', 0):.0f}ms
- **Tools Used:** {', '.join(react.get('tools_used', [])) or 'None'}
- **Steps:** {len(workflow.get('steps', []))}
- **Intent Detected:** {workflow.get('intent_detected', 'N/A')}

**Workflow Steps:**
{format_workflow_steps(workflow)}

**Response Preview:**
> {react.get('response', 'N/A')[:200]}...

"""
        else:
            report += f"""- **Status:** ❌ Failed
- **Error:** {react.get('error', 'Unknown')}

"""
        
        report += "---\n\n"
    
    # Comparison analysis
    report += """## Analysis

### Tool Usage Comparison

| Test | Single Mode Tools | ReAct Mode Tools | ReAct Steps |
|------|-------------------|------------------|-------------|
"""
    
    for single, react in zip(single_results, react_results):
        test_id = single.get("test_id", "?")
        single_tools = ", ".join(single.get("tools_used", [])) if single.get("success") else "❌"
        react_tools = ", ".join(react.get("tools_used", [])) if react.get("success") else "❌"
        react_steps = len(react.get("workflow", {}).get("steps", [])) if react.get("success") else 0
        report += f"| {test_id} | {single_tools} | {react_tools} | {react_steps} |\n"
    
    report += """

### Key Observations

1. **Multi-tool queries**: ReAct mode can chain multiple tools for complex queries
2. **Single-tool queries**: Both modes perform similarly for simple queries
3. **Reasoning steps**: ReAct mode shows explicit reasoning before each tool call

"""
    
    return report


async def main():
    """Main test runner."""
    print("=" * 60)
    print("LocalMate Agent Mode Comparison Test")
    print("=" * 60)
    print()
    
    single_results = []
    react_results = []
    
    async with httpx.AsyncClient() as client:
        # Test Single Mode
        print(f"📌 Running Single Mode Tests ({SINGLE_MODE_DELAY}s delay)...")
        print("-" * 40)
        
        for test in TEST_CASES:
            print(f"  Test {test['id']}: {test['query'][:40]}...")
            result = await run_test(client, test, react_mode=False)
            single_results.append(result)
            
            status = "✅" if result.get("success") else "❌"
            tools = ", ".join(result.get("tools_used", [])) or "None"
            print(f"    {status} Tools: {tools} | {result.get('api_duration_ms', 0):.0f}ms")
            
            if test["id"] < len(TEST_CASES):
                await asyncio.sleep(SINGLE_MODE_DELAY)
        
        print()
        print(f"⏸️  Waiting {MODE_SWITCH_DELAY}s before ReAct mode...")
        await asyncio.sleep(MODE_SWITCH_DELAY)
        
        # Test ReAct Mode
        print()
        print(f"🧠 Running ReAct Mode Tests ({REACT_MODE_DELAY}s delay)...")
        print("-" * 40)
        
        for test in TEST_CASES:
            print(f"  Test {test['id']}: {test['query'][:40]}...")
            result = await run_test(client, test, react_mode=True)
            react_results.append(result)
            
            status = "✅" if result.get("success") else "❌"
            tools = ", ".join(result.get("tools_used", [])) or "None"
            steps = len(result.get("workflow", {}).get("steps", []))
            print(f"    {status} Tools: {tools} | Steps: {steps} | {result.get('api_duration_ms', 0):.0f}ms")
            
            if test["id"] < len(TEST_CASES):
                await asyncio.sleep(REACT_MODE_DELAY)
    
    # Generate report
    print()
    print("📝 Generating report...")
    report = generate_report(single_results, react_results)
    
    # Use absolute path based on script location
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, "react_comparison_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Report saved to: {report_path}")
    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
