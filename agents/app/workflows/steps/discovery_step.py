"""Discovery step and modular sources for gathering candidates from multiple channels."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.app.services.feed_ingestion import FeedIngestionService
from backend.app.services.whitelist import WhitelistService
from agents.app.tools.searxng_tool import run_discovery_matrix


class DiscoverySource(ABC):
    """Abstract base class for candidate discovery sources (Open/Closed Principle)."""

    @abstractmethod
    async def discover(self) -> List[Dict[str, Any]]:
        """Fetch candidates from this source."""
        ...


class RSSDiscoverySource(DiscoverySource):
    """Ingests from whitelisted RSS/Atom feeds."""

    async def discover(self) -> List[Dict[str, Any]]:
        return await FeedIngestionService.ingest_whitelisted_feeds(max_items_per_feed=3)


class ArxivDiscoverySource(DiscoverySource):
    """Ingests academic preprints via ArXiv API."""

    async def discover(self) -> List[Dict[str, Any]]:
        return await FeedIngestionService.ingest_arxiv_preprints(max_results=5)


class RedditDiscoverySource(DiscoverySource):
    """Ingests community pulse and breakthroughs from Reddit."""

    async def discover(self) -> List[Dict[str, Any]]:
        return await FeedIngestionService.ingest_reddit_pulse(min_score=100)


class SearXNGDiscoverySource(DiscoverySource):
    """Ingests candidate leads from SearXNG metasearch discovery matrix."""

    async def discover(self) -> List[Dict[str, Any]]:
        searx_results = await run_discovery_matrix()
        leads = []
        for r in searx_results:
            url = r.get("url", "").strip()
            if url:
                wl_entry = WhitelistService.get_source_for_url(url)
                leads.append({
                    "url": url,
                    "raw_url": r.get("raw_url", url),
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "publisher": wl_entry.domain if wl_entry else r.get("engine", "web"),
                    "tier": wl_entry.tier if wl_entry else "Tier 3",
                    "category": wl_entry.category if wl_entry else "General AI",
                    "source_type": "searxng",
                    "ingestion_strategy": wl_entry.ingestion_strategy if wl_entry else "direct_scrape",
                })
        return leads


class DiscoveryStep:
    """Orchestrates candidate discovery across registered sources."""

    def __init__(self, live: bool = False, sources: Optional[List[DiscoverySource]] = None):
        self.live = live
        self.sources = sources or [
            RSSDiscoverySource(),
            ArxivDiscoverySource(),
            RedditDiscoverySource(),
            SearXNGDiscoverySource(),
        ]

    async def execute(self, sample_candidates: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Discover candidate leads from registered discovery sources or return sample candidates."""
        if self.live:
            seen_urls = set()
            leads = []
            for src in self.sources:
                items = await src.discover()
                for item in items:
                    norm_url = item.get("url", "")
                    if norm_url and norm_url not in seen_urls:
                        seen_urls.add(norm_url)
                        leads.append(item)
            return leads[:35]
        elif sample_candidates:
            return sample_candidates
        else:
            from scripts.simulate_editorial_run import DEMO_CANDIDATES, REJECTED_SAMPLE_CANDIDATES
            return DEMO_CANDIDATES + REJECTED_SAMPLE_CANDIDATES
