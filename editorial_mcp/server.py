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
APP_HOST = os.getenv("APP_HOST", "192.168.1.101")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = os.getenv("AINEWS_BACKEND_URL", f"http://{APP_HOST}:{BACKEND_PORT}/api").rstrip("/")
try:
    from backend.app.core.config import settings
    EDITORIAL_TOKEN = os.getenv("EDITORIAL_SECRET_KEY") or settings.EDITORIAL_SECRET_KEY
except Exception:
    EDITORIAL_TOKEN = os.getenv("EDITORIAL_SECRET_KEY") or os.getenv("EDITORIAL_API_TOKEN", "editorial_secret_token_change_in_production")

# Initialize MCP Server
mcp_server = mcp = MCPServer(
    name="AI Industry News Editorial Interface",
    version="2.0.0",
    instructions="Editorial interface for AI Industry News Daily. Exposes editorial context, candidate submission, draft staging, publication gate verification, and reader feedback analytics."
)


def _get_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {EDITORIAL_TOKEN}",
        "Content-Type": "application/json",
    }


async def _request_with_retry(
    method: str,
    path: str,
    *,
    timeout: float = 20.0,
    max_retries: int = 4,
    **kwargs
) -> httpx.Response:
    """
    Execute an HTTP request against the FastAPI backend with exponential backoff
    to handle transient connection failures, service boots, or timeouts.
    """
    url = f"{API_BASE_URL}/{path.lstrip('/')}"
    headers = _get_headers()
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))

    last_error: Optional[Exception] = None
    delays = [1.0, 2.0, 4.0, 8.0]

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.request(method, url, headers=headers, **kwargs)
                # If we get a transient server gateway error, treat as retryable
                if res.status_code in (502, 503, 504) and attempt < max_retries - 1:
                    delay = delays[min(attempt, len(delays) - 1)]
                    logger.warning(
                        f"Backend returned HTTP {res.status_code} for {method} {url}. Retrying in {delay}s (attempt {attempt+1}/{max_retries})..."
                    )
                    await asyncio.sleep(delay)
                    continue
                return res
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            last_error = exc
            if attempt < max_retries - 1:
                delay = delays[min(attempt, len(delays) - 1)]
                logger.warning(
                    f"Connection to backend {url} failed: {exc}. Retrying in {delay}s (attempt {attempt+1}/{max_retries})..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"Exhausted {max_retries} attempts connecting to backend at {url}: {exc}")
                raise

    if last_error:
        raise last_error
    raise RuntimeError(f"Request failed after {max_retries} attempts")


@mcp_server.tool()
async def get_editorial_context(lookback_days: int = 28, days_lookback: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch editorial context including recent coverage topics, repetition warnings,
    and active scoring weights from PostgreSQL memory.
    """
    eff_days = days_lookback if days_lookback is not None else lookback_days
    res = await _request_with_retry(
        "POST",
        "/editorial/context",
        json={"lookback_days": eff_days},
        timeout=20.0
    )
    res.raise_for_status()
    return res.json()


@mcp_server.tool()
async def get_feedback_analytics(window_days: int = 30) -> Dict[str, Any]:
    """
    Retrieve aggregated reader feedback analytics, category approval ratings,
    and cold-start bias status.
    """
    res = await _request_with_retry(
        "GET",
        "/editorial/feedback-analytics",
        params={"window_days": window_days},
        timeout=20.0
    )
    res.raise_for_status()
    return res.json()


@mcp_server.tool()
async def get_historical_feedback(limit: int = 50, days: int = 30) -> List[Dict[str, Any]]:
    """
    Retrieve story-level upvote/downvote interaction history across recent editions.
    """
    res = await _request_with_retry(
        "GET",
        "/editorial/feedback-history",
        params={"limit": limit, "days": days},
        timeout=20.0
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
    res = await _request_with_retry(
        "GET",
        "/editorial/memory",
        params=params,
        timeout=20.0
    )
    res.raise_for_status()
    return res.json()


@mcp_server.tool()
async def submit_candidate_stories(
    candidates: List[Dict[str, Any]],
    run_id: Optional[str] = None,
    clear_existing: bool = True,
    edition_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Record discovered candidate stories with multi-factor dimensional scores and
    explicit rejection reasons into the publication audit trail.
    """
    payload = {
        "candidates": candidates,
        "run_id": run_id,
        "clear_existing": clear_existing,
        "edition_date": edition_date,
    }
    res = await _request_with_retry(
        "POST",
        "/editorial/candidates",
        json=payload,
        timeout=45.0
    )
    res.raise_for_status()
    return res.json()


@mcp_server.tool()
async def get_candidate_details(candidate_id: str) -> Dict[str, Any]:
    """
    Retrieve full research metadata, scores, and rejection rationale for a specific candidate story.
    """
    res = await _request_with_retry(
        "GET",
        f"/editorial/candidates/{candidate_id}",
        timeout=20.0
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
    res = await _request_with_retry(
        "POST",
        "/editorial/draft",
        json=payload,
        timeout=45.0
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
    res = await _request_with_retry(
        "GET",
        f"/editorial/edition/{edition_id}/status",
        timeout=20.0
    )
    res.raise_for_status()
    return res.json()


@mcp_server.tool()
async def publish_edition(edition_id: str) -> Dict[str, Any]:
    """
    Publish an approved edition to intranet readers after deterministic gate verification.
    """
    res = await _request_with_retry(
        "POST",
        f"/editorial/edition/{edition_id}/publish",
        timeout=20.0
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
    res = await _request_with_retry(
        "POST",
        f"/editorial/edition/{edition_id}/unpublish",
        timeout=20.0
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
    res = await _request_with_retry(
        "POST",
        "/editorial/override",
        json=payload,
        timeout=20.0
    )
    res.raise_for_status()
    return res.json()


def main():
    """Run MCP server over standard stdio."""
    mcp_server.run()


if __name__ == "__main__":
    main()
