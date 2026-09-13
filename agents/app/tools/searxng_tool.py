"""ADK Tool for SearXNG Web Search."""

from typing import Optional, List, Dict, Any
from backend.app.services.searxng import SearXNGClient
from agents.app.config import SEARXNG_URL

_client = SearXNGClient(base_url=SEARXNG_URL)

async def search_web(
    query: str,
    categories: str = "general",
    time_range: str = "day",
    pageno: int = 1
) -> List[Dict[str, Any]]:
    """Search the web via SearXNG metasearch engine.

    Args:
        query: The search query string.
        categories: Comma-separated categories (e.g. 'general', 'news', 'science').
        time_range: Filter by time ('day', 'week', 'month', 'year').
        pageno: Results page number.

    Returns:
        List of search result dictionaries containing title, url, snippet, engine, etc.
    """
    return await _client.search(query=query, categories=categories, time_range=time_range, pageno=pageno)

async def run_discovery_matrix(
    focus_areas: Optional[List[str]] = None,
    queries: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Run the automated multi-query discovery matrix across key AI ecosystem topics.

    Args:
        focus_areas: Optional list of specific topic areas to focus on.
        queries: Alias for focus_areas.

    Returns:
        Deduplicated list of candidate news items and articles found.
    """
    target = queries or focus_areas
    return await _client.run_discovery_matrix(queries=target)
