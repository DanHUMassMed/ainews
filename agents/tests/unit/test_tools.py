"""Unit tests for ADK Agent configuration and tool wrappers."""

import pytest
from unittest.mock import patch, AsyncMock
from agents.app.config import normalize_model_name, get_agent_model, DEFAULT_LLM_MODEL
from agents.app.tools import (
    search_web,
    run_discovery_matrix,
    scrape_webpage,
    get_editorial_context,
    get_feedback_analytics,
    get_historical_feedback,
    fetch_editorial_memory,
    submit_candidate_stories,
    get_candidate_details,
    stage_edition_draft,
    get_edition_status,
    publish_edition,
    unpublish_edition,
    record_editorial_override,
)
from google.adk.agents import LlmAgent

def test_config_model_normalization():
    assert normalize_model_name("deepseek/deepseek-v4-flash-0731") == "openrouter/deepseek/deepseek-v4-flash-0731"
    assert normalize_model_name("openrouter/deepseek/deepseek-v4-flash-0731") == "openrouter/deepseek/deepseek-v4-flash-0731"
    assert normalize_model_name("anthropic/claude-3-5-sonnet") == "openrouter/anthropic/claude-3-5-sonnet"

def test_get_agent_model():
    model = get_agent_model("discovery")
    assert model.startswith("openrouter/")

@pytest.mark.asyncio
async def test_searxng_tool():
    with patch("agents.app.tools.searxng_tool._client.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"title": "AI Breakthrough", "url": "https://example.com/ai"}]
        res = await search_web(query="test", categories="news", time_range="day")
        assert len(res) == 1
        assert res[0]["title"] == "AI Breakthrough"
        mock_search.assert_awaited_once_with(query="test", categories="news", time_range="day", pageno=1)

@pytest.mark.asyncio
async def test_searxng_discovery_matrix_tool():
    with patch("agents.app.tools.searxng_tool._client.run_discovery_matrix", new_callable=AsyncMock) as mock_matrix:
        mock_matrix.return_value = [{"title": "Matrix Item", "url": "https://example.com/item"}]
        res = await run_discovery_matrix(queries=["LLMs"])
        assert len(res) == 1
        mock_matrix.assert_awaited_once_with(queries=["LLMs"])

@pytest.mark.asyncio
async def test_firecrawl_tool():
    with patch("agents.app.tools.firecrawl_tool._client.scrape_url", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = {"markdown": "# Article", "title": "Scraped Article"}
        res = await scrape_webpage(url="https://example.com/article")
        assert res["markdown"] == "# Article"
        mock_scrape.assert_awaited_once_with(url="https://example.com/article", formats=["markdown"], only_main_content=True)

@pytest.mark.asyncio
async def test_mcp_editorial_context_tool():
    with patch("agents.app.tools.editorial_mcp_tool._client.get_editorial_context", new_callable=AsyncMock) as mock_ctx:
        mock_ctx.return_value = {"active_edition": None, "feedback_summary": {}}
        res = await get_editorial_context(lookback_days=14)
        assert "feedback_summary" in res
        mock_ctx.assert_awaited_once_with(lookback_days=14)

@pytest.mark.asyncio
async def test_mcp_submit_candidates_tool():
    with patch("agents.app.tools.editorial_mcp_tool._client.submit_candidate_stories", new_callable=AsyncMock) as mock_submit:
        mock_submit.return_value = {"status": "success", "count": 1}
        candidates = [{"title": "Candidate 1", "url": "https://example.com/1", "score": 9.0}]
        res = await submit_candidate_stories(candidates)
        assert res["status"] == "success"
        mock_submit.assert_awaited_once_with(candidates=candidates, run_id=None, clear_existing=True, edition_date=None)

@pytest.mark.asyncio
async def test_mcp_stage_edition_tool():
    with patch("agents.app.tools.editorial_mcp_tool._client.stage_edition_draft", new_callable=AsyncMock) as mock_stage:
        mock_stage.return_value = {"status": "staged", "edition_id": "test-id"}
        res = await stage_edition_draft(date="2026-09-08", title="Daily Briefing")
        assert res["edition_id"] == "test-id"
        mock_stage.assert_awaited_once_with(
            date="2026-09-08",
            title="Daily Briefing",
            introduction="",
            low_signal_notice=None,
            stories=[],
        )

def test_adk_agent_tool_binding():
    # Verify Google ADK LlmAgent binds all our tools cleanly without schema or registration errors
    agent = LlmAgent(
        name="EditorialAgent",
        model=get_agent_model("discovery"),
        instruction="You are an editorial agent.",
        tools=[
            search_web,
            run_discovery_matrix,
            scrape_webpage,
            get_editorial_context,
            get_feedback_analytics,
            get_historical_feedback,
            fetch_editorial_memory,
            submit_candidate_stories,
            get_candidate_details,
            stage_edition_draft,
            get_edition_status,
            publish_edition,
            unpublish_edition,
            record_editorial_override,
        ],
    )
    assert len(agent.tools) == 14
    assert agent.name == "EditorialAgent"
