"""ADK Tool for Whitelisted Feed Ingestion.

Enables ADK Discovery and Research agents to ingest clean, verified candidate
leads directly from whitelisted RSS/Atom feeds, ArXiv API, and community pulses.
"""

from typing import List, Dict, Any, Optional
from backend.app.services.feed_ingestion import FeedIngestionService

async def ingest_whitelisted_feeds(max_items_per_feed: int = 5) -> List[Dict[str, Any]]:
    """Concurrently ingests candidate story leads from all active whitelisted RSS/Atom feeds.

    Returns:
        List of candidate lead dictionaries containing title, canonical url,
        snippet, published_date, hero image_url, and publisher tier metadata.
    """
    return await FeedIngestionService.ingest_whitelisted_feeds(max_items_per_feed=max_items_per_feed)

async def ingest_arxiv_preprints(categories: str = "cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG", max_results: int = 15) -> List[Dict[str, Any]]:
    """Queries the structured ArXiv API for recent foundational AI preprints."""
    return await FeedIngestionService.ingest_arxiv_preprints(categories=categories, max_results=max_results)

async def ingest_community_pulse(subreddit: str = "LocalLLaMA", min_score: int = 100) -> List[Dict[str, Any]]:
    """Queries high-signal community breakthroughs filtered by upvote thresholds."""
    return await FeedIngestionService.ingest_reddit_pulse(subreddit=subreddit, min_score=min_score)
