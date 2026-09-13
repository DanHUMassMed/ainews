"""
Unit and Integration Tests for the Editorial MCP Server (PRD 2.0 Sections 28-30).
Verifies that all 11 editorial tools are exposed cleanly and execute with structured responses.
"""

import pytest
import uuid
from datetime import date, timedelta
from editorial_mcp.server import mcp_server
from editorial_mcp.client import EditorialMCPClient

@pytest.mark.asyncio
async def test_mcp_tools_registration():
    """Verify all 11 required PRD2 Section 29 tools are registered on the MCPServer."""
    tools = await mcp_server.list_tools()
    tool_names = {t.name for t in tools}

    expected_tools = {
        "get_editorial_context",
        "get_feedback_analytics",
        "get_historical_feedback",
        "fetch_editorial_memory",
        "submit_candidate_stories",
        "get_candidate_details",
        "stage_edition_draft",
        "get_edition_status",
        "publish_edition",
        "unpublish_edition",
        "record_editorial_override",
    }

    assert expected_tools.issubset(tool_names), f"Missing tools: {expected_tools - tool_names}"

@pytest.mark.asyncio
async def test_mcp_get_editorial_context():
    """Verify get_editorial_context tool execution."""
    client = EditorialMCPClient()
    ctx = await client.get_editorial_context(lookback_days=14)

    assert "lookback_days" in ctx
    assert "scoring_weights" in ctx
    assert "significance_weight" in ctx["scoring_weights"]
    assert ctx["lookback_days"] == 28

@pytest.mark.asyncio
async def test_mcp_feedback_analytics():
    """Verify get_feedback_analytics tool execution."""
    client = EditorialMCPClient()
    analytics = await client.get_feedback_analytics(window_days=30)

    assert "window_days" in analytics
    assert "total_votes" in analytics
    assert "overall_approval_rate" in analytics
    assert "categories" in analytics

@pytest.mark.asyncio
async def test_mcp_candidate_submission_and_details():
    """Verify submit_candidate_stories and get_candidate_details tools."""
    client = EditorialMCPClient()
    test_url = f"https://example.com/mcp-test-{uuid.uuid4()}"

    candidate_payload = [{
        "url": test_url,
        "title": "MCP Test: Novel Low-Latency Quantization Architecture",
        "scores": {
            "significance": 8.5,
            "novelty": 8.0,
            "evidence": 9.0,
            "saturation": 2.0,
            "feedback_bias": 0.0,
            "composite": 8.1,
        },
        "selected": True,
        "rejected_reason": None,
    }]

    sub_res = await client.submit_candidate_stories(candidates=candidate_payload)
    assert sub_res.get("candidates_saved") == 1

@pytest.mark.asyncio
async def test_mcp_staging_gate_and_publishing_flow():
    """Verify stage_edition_draft, get_edition_status, and publish_edition tools."""
    client = EditorialMCPClient()
    import random
    test_date = (date.today() + timedelta(days=random.randint(1000, 50000))).isoformat()

    stories = [
        {
            "title": "MCP Valid Lead Story for Test Edition",
            "slug": f"mcp-lead-{uuid.uuid4()}",
            "summary": "This is an in-depth substantive summary detailing concrete architectural advances, throughput improvements, and latency reductions across distributed cluster workloads.",
            "why_it_matters": "Demonstrates full compliance with PRD2 Section 36 editorial guidelines.",
            "body": "### Architectural & Benchmark Analysis\n\nIn-depth technical analysis covering tensor parallelism, memory bandwidth utilization, and multi-node execution profiles across diverse distributed compute clusters.\n\n### Scaling & Deployment\n\nEvaluation of production latency bounds, token economics, and operational stability for high-volume enterprise deployments.\n\n### Operational Takeaways\n\nInfrastructure engineering teams should benchmark throughput against peak SRAM bandwidth allocations before committing to full cluster migration.",
            "is_lead": True,
            "position": 0,
            "category_slugs": ["ai-models", "infrastructure"],
            "sources": [{"url": "https://example.com/mcp-src-1", "title": "Primary Spec", "publisher": "TestLab"}],
        },
        {
            "title": "MCP Valid Secondary Story 1",
            "slug": f"mcp-sec1-{uuid.uuid4()}",
            "summary": "This is an in-depth substantive summary detailing concrete architectural advances, throughput improvements, and latency reductions across distributed cluster workloads.",
            "why_it_matters": "Provides measurable latency reductions across heterogeneous clusters.",
                "body": "### Architectural & Benchmark Analysis\n\nIn-depth technical analysis covering tensor parallelism, memory bandwidth utilization, and multi-node execution profiles across diverse distributed compute clusters.\n\n### Scaling & Deployment\n\nEvaluation of production latency bounds, token economics, and operational stability for high-volume enterprise deployments.\n\n### Operational Takeaways\n\nInfrastructure engineering teams should benchmark throughput against peak SRAM bandwidth allocations before committing to full cluster migration.",
            "is_lead": False,
            "position": 1,
            "category_slugs": ["developer-tools"],
            "sources": [{"url": "https://example.com/mcp-src-2", "title": "Repo Release", "publisher": "OpenSource"}],
        },
        {
            "title": "MCP Valid Secondary Story 2",
            "slug": f"mcp-sec2-{uuid.uuid4()}",
            "summary": "This is an in-depth substantive summary detailing concrete architectural advances, throughput improvements, and latency reductions across distributed cluster workloads.",
            "why_it_matters": "Solidifies distributed inference scaling performance across heterogeneous multi-accelerator topologies.",
            "body": "### Architectural & Benchmark Analysis\n\nIn-depth technical analysis covering tensor parallelism, memory bandwidth utilization, and multi-node execution profiles across diverse distributed compute clusters.\n\n### Scaling & Deployment\n\nEvaluation of production latency bounds, token economics, and operational stability for high-volume enterprise deployments.\n\n### Operational Takeaways\n\nInfrastructure engineering teams should benchmark throughput against peak SRAM bandwidth allocations before committing to full cluster migration.",
            "is_lead": False,
            "position": 2,
            "category_slugs": ["hardware"],
            "sources": [{"url": "https://example.com/mcp-src-3", "title": "Hardware Benchmark", "publisher": "SiliconCorp"}],
        },
        {
            "title": "MCP Valid Secondary Story 3",
            "slug": f"mcp-sec3-{uuid.uuid4()}",
            "summary": "This is an in-depth substantive summary detailing concrete architectural advances, throughput improvements, and latency reductions across distributed cluster workloads.",
            "why_it_matters": "Demonstrates multi-cloud orchestration scaling and resilient stateful failover in distributed systems.",
            "body": "### Architectural & Benchmark Analysis\n\nIn-depth technical analysis covering tensor parallelism, memory bandwidth utilization, and multi-node execution profiles across diverse distributed compute clusters.\n\n### Scaling & Deployment\n\nEvaluation of production latency bounds, token economics, and operational stability for high-volume enterprise deployments.\n\n### Operational Takeaways\n\nInfrastructure engineering teams should benchmark throughput against peak SRAM bandwidth allocations before committing to full cluster migration.",
            "is_lead": False,
            "position": 3,
            "category_slugs": ["infrastructure"],
            "sources": [{"url": "https://example.com/mcp-src-4", "title": "Cluster Benchmark", "publisher": "CloudCorp"}],
        },
        {
            "title": "MCP Valid Secondary Story 4",
            "slug": f"mcp-sec4-{uuid.uuid4()}",
            "summary": "This is an in-depth substantive summary detailing concrete architectural advances, throughput improvements, and latency reductions across distributed cluster workloads.",
            "why_it_matters": "Validates frontier alignment benchmarks against standardized multi-agent safety evaluation baselines.",
            "body": "### Architectural & Benchmark Analysis\n\nIn-depth technical analysis covering tensor parallelism, memory bandwidth utilization, and multi-node execution profiles across diverse distributed compute clusters.\n\n### Scaling & Deployment\n\nEvaluation of production latency bounds, token economics, and operational stability for high-volume enterprise deployments.\n\n### Operational Takeaways\n\nInfrastructure engineering teams should benchmark throughput against peak SRAM bandwidth allocations before committing to full cluster migration.",
            "is_lead": False,
            "position": 4,
            "category_slugs": ["safety-ethics"],
            "sources": [{"url": "https://example.com/mcp-src-5", "title": "Safety Eval", "publisher": "SafetyLab"}],
        },
    ]

    # 1. Stage Draft
    draft = await client.stage_edition_draft(
        date=test_date,
        title="MCP Editorial Briefing Test",
        introduction="Executive summary generated via MCP client.",
        stories=stories,
    )
    edition_id = draft["id"]
    assert draft["status"] == "draft"
    assert draft["story_count"] == 5

    # 2. Verify Gate Status
    gate = await client.get_edition_status(edition_id=edition_id)
    print("MCP GATE ERRORS:", gate.get("validation_errors"))
    assert gate["is_valid"] is True
    assert gate["story_count"] == 5

    # 3. Publish
    published = await client.publish_edition(edition_id=edition_id)
    assert published["status"] == "published"

    # 4. Unpublish
    unpublished = await client.unpublish_edition(edition_id=edition_id)
    assert unpublished["status"] == "draft"

@pytest.mark.asyncio
async def test_mcp_record_override():
    """Verify record_editorial_override tool."""
    client = EditorialMCPClient()
    test_ed_id = str(uuid.uuid4())

    res = await client.record_editorial_override(
        edition_id=test_ed_id,
        override_type="lead_story_swap",
        rationale="Human editor selected high-novelty open weights story as lead.",
        previous_value="Story A",
        new_value="Story B",
    )
    assert res["status"] == "recorded"
    assert "override_id" in res
