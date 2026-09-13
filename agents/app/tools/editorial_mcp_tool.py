"""ADK Tools for Editorial MCP Operations.

Exposes all 11 Editorial MCP tools to ADK agents using the decoupled Editorial MCP Client.
"""

from typing import Optional, List, Dict, Any
from editorial_mcp.client import EditorialMCPClient

_client = EditorialMCPClient()

async def get_editorial_context(lookback_days: int = 28) -> Dict[str, Any]:
    """Retrieve system-wide editorial context including current active edition, guidelines, and feedback summaries."""
    return await _client.get_editorial_context(lookback_days=lookback_days)

async def get_feedback_analytics(window_days: int = 30) -> Dict[str, Any]:
    """Retrieve aggregate reader feedback analytics, vote ratios, and top performing stories."""
    return await _client.get_feedback_analytics(window_days=window_days)

async def get_historical_feedback(limit: int = 50, days: int = 30) -> List[Dict[str, Any]]:
    """Retrieve granular historical feedback entries to calibrate editorial selection and critique."""
    return await _client.get_historical_feedback(limit=limit, days=days)

async def fetch_editorial_memory(memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve editorial guidelines, voice constraints, blacklist domains, and precedent rules."""
    return await _client.fetch_editorial_memory(memory_type=memory_type)

async def submit_candidate_stories(candidates: List[Dict[str, Any]], run_id: Optional[str] = None) -> Dict[str, Any]:
    """Submit evaluated candidate stories for editorial pipeline ingestion.

    Each candidate should have:
        title (str), url (str), summary (str), why_it_matters (str),
        score (float), tier (str), primary_category (str).
    """
    return await _client.submit_candidate_stories(candidates=candidates, run_id=run_id)

async def get_candidate_details(candidate_id: str) -> Dict[str, Any]:
    """Retrieve full evaluation details, scores, and source content for a candidate story."""
    return await _client.get_candidate_details(candidate_id=candidate_id)

async def stage_edition_draft(
    date: str,
    title: str = "",
    introduction: str = "",
    low_signal_notice: Optional[str] = None,
    stories: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Stage a structured daily edition draft containing selected stories."""
    return await _client.stage_edition_draft(
        date=date,
        title=title,
        introduction=introduction,
        low_signal_notice=low_signal_notice,
        stories=stories or [],
    )

async def get_edition_status(edition_id: str) -> Dict[str, Any]:
    """Check publishing status and story contents of a specific edition draft."""
    return await _client.get_edition_status(edition_id=edition_id)

async def publish_edition(edition_id: str) -> Dict[str, Any]:
    """Publish a staged edition draft to make it live for readers."""
    return await _client.publish_edition(edition_id=edition_id)

async def unpublish_edition(edition_id: str) -> Dict[str, Any]:
    """Unpublish an edition and revert it back to draft status."""
    return await _client.unpublish_edition(edition_id=edition_id)

async def record_editorial_override(
    edition_id: str,
    story_id: Optional[str] = None,
    override_type: str = "manual_override",
    rationale: str = "",
    previous_value: Optional[str] = None,
    new_value: Optional[str] = None
) -> Dict[str, Any]:
    """Record an explicit human or algorithmic editorial override with audit trail rationale."""
    return await _client.record_editorial_override(
        edition_id=edition_id,
        story_id=story_id,
        override_type=override_type,
        rationale=rationale,
        previous_value=previous_value,
        new_value=new_value
    )
