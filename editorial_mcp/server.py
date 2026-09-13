"""
AI Industry News Daily - Editorial Model Context Protocol (MCP) Server
PRD 2.0 Sections 28-30: Framework-agnostic MCP server exposing all editorial operations
to Google ADK 2.x, human conversational editors, or external agent runtimes.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ainews.editorial_mcp")
import httpx
from mcp.server.mcpserver import MCPServer

# Configuration
API_BASE_URL = os.getenv("AINEWS_BACKEND_URL", "http://127.0.0.1:8000/api")
try:
    from backend.app.core.config import settings
    EDITORIAL_TOKEN = os.getenv("EDITORIAL_SECRET_KEY") or settings.EDITORIAL_SECRET_KEY
except Exception:
    EDITORIAL_TOKEN = os.getenv("EDITORIAL_SECRET_KEY") or os.getenv("EDITORIAL_API_TOKEN", "editorial_secret_token_change_in_production")

# Initialize MCP Server
mcp_server = MCPServer(
    name="AI Industry News Editorial Interface",
    version="2.0.0",
    instructions="Editorial interface for AI Industry News Daily. Exposes editorial context, candidate submission, draft staging, publication gate verification, and reader feedback analytics."
)


def _get_client(timeout: float = 15.0):
    return httpx.AsyncClient(timeout=timeout), API_BASE_URL

def _get_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {EDITORIAL_TOKEN}",
        "Content-Type": "application/json",
    }

@mcp_server.tool()
async def get_editorial_context(lookback_days: int = 28, days_lookback: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch editorial context including recent coverage topics, repetition warnings,
    and active scoring weights from PostgreSQL memory.
    """
    eff_days = days_lookback if days_lookback is not None else lookback_days
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.post(
            f"{base_url}/editorial/context",
            headers=_get_headers(),
            json={"lookback_days": eff_days},
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def get_feedback_analytics(window_days: int = 30) -> Dict[str, Any]:
    """
    Retrieve aggregated reader feedback analytics, category approval ratings,
    and cold-start bias status.
    """
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.get(
            f"{base_url}/editorial/feedback-analytics",
            headers=_get_headers(),
            params={"window_days": window_days},
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def get_historical_feedback(limit: int = 50, days: int = 30) -> List[Dict[str, Any]]:
    """
    Retrieve story-level upvote/downvote interaction history across recent editions.
    """
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.get(
            f"{base_url}/editorial/feedback-history",
            headers=_get_headers(),
            params={"limit": limit, "days": days},
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def fetch_editorial_memory(memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch persistent editorial learnings, durable rules, and topic patterns.
    """
    params = {}
    if memory_type:
        params["memory_type"] = memory_type
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.get(
            f"{base_url}/editorial/memory",
            headers=_get_headers(),
            params=params,
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def submit_candidate_stories(candidates: List[Dict[str, Any]], run_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Record discovered candidate stories with multi-factor dimensional scores and
    explicit rejection reasons into the publication audit trail.
    """
    payload = {
        "candidates": candidates,
        "run_id": run_id,
    }
    client, base_url = _get_client(30.0)
    async with client:
        res = await client.post(
            f"{base_url}/editorial/candidates",
            headers=_get_headers(),
            json=payload,
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def get_candidate_details(candidate_id: str) -> Dict[str, Any]:
    """
    Retrieve full research metadata, scores, and rejection rationale for a specific candidate story.
    """
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.get(
            f"{base_url}/editorial/candidates/{candidate_id}",
            headers=_get_headers(),
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def stage_edition_draft(
    date: str,
    title: str,
    introduction: Optional[str] = None,
    low_signal_notice: Optional[str] = None,
    stories: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Stage an edition draft containing selected lead and secondary stories with
    'Why It Matters' callouts and source citations.
    """
    payload = {
        "date": date,
        "title": title,
        "introduction": introduction or "",
        "low_signal_notice": low_signal_notice,
        "stories": stories or [],
    }
    client, base_url = _get_client(30.0)
    async with client:
        res = await client.post(
            f"{base_url}/editorial/draft",
            headers=_get_headers(),
            json=payload,
        )
        if res.status_code >= 400:
            logger.error(f"Failed to stage draft ({res.status_code}): {res.text}")
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def get_edition_status(edition_id: str) -> Dict[str, Any]:
    """
    Check draft compliance with deterministic publication gate rules (PRD Section 27 & 36).
    Returns gate compliance status, story count, lead count, and any validation errors.
    """
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.get(
            f"{base_url}/editorial/edition/{edition_id}/status",
            headers=_get_headers(),
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def publish_edition(edition_id: str) -> Dict[str, Any]:
    """
    Publish an approved edition to intranet readers after deterministic gate verification.
    """
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.post(
            f"{base_url}/editorial/edition/{edition_id}/publish",
            headers=_get_headers(),
        )
        if res.status_code >= 400:
            logger.error(f"Failed to publish edition ({res.status_code}): {res.text}")
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def unpublish_edition(edition_id: str) -> Dict[str, Any]:
    """
    Revert a published edition back to draft state for editorial modifications.
    """
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.post(
            f"{base_url}/editorial/edition/{edition_id}/unpublish",
            headers=_get_headers(),
        )
        res.raise_for_status()
        return res.json()

@mcp_server.tool()
async def record_editorial_override(
    edition_id: str,
    story_id: Optional[str] = None,
    override_type: str = "manual_override",
    rationale: str = "",
    previous_value: Optional[str] = None,
    new_value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log an editorial override event to the permanent audit trail when a human or agent
    replaces a lead story, rejects a high-ranked candidate, or modifies editorial copy.
    """
    payload = {
        "edition_id": edition_id,
        "story_id": story_id,
        "override_type": override_type,
        "rationale": rationale,
        "previous_value": previous_value,
        "new_value": new_value,
    }
    client, base_url = _get_client(15.0)
    async with client:
        res = await client.post(
            f"{base_url}/editorial/override",
            headers=_get_headers(),
            json=payload,
        )
        res.raise_for_status()
        return res.json()

def main():
    """Run MCP server over standard stdio."""
    mcp_server.run()

if __name__ == "__main__":
    main()
