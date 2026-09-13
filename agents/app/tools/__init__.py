"""ADK Tools for AI News Agents."""

from agents.app.tools.searxng_tool import search_web, run_discovery_matrix
from agents.app.tools.firecrawl_tool import scrape_webpage
from agents.app.tools.feed_tool import (
    ingest_whitelisted_feeds,
    ingest_arxiv_preprints,
    ingest_community_pulse,
)
from agents.app.tools.whitelist_tool import (
    check_whitelist_status,
    get_whitelisted_sources,
)
from agents.app.tools.editorial_mcp_tool import (
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

__all__ = [
    "search_web",
    "run_discovery_matrix",
    "scrape_webpage",
    "ingest_whitelisted_feeds",
    "ingest_arxiv_preprints",
    "ingest_community_pulse",
    "check_whitelist_status",
    "get_whitelisted_sources",
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
]
