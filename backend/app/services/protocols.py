"""Service Protocols (Interfaces) defining contracts for key application dependencies."""

from typing import Protocol, List, Dict, Any, Optional, runtime_checkable
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.candidate import CandidateStory


@runtime_checkable
class SearchService(Protocol):
    """Protocol for search engines."""
    async def search(
        self,
        query: str,
        time_range: str = "day",
        max_results: int = 40,
        categories: str = "general,it,science",
    ) -> List[Dict[str, Any]]: ...


@runtime_checkable
class ScraperService(Protocol):
    """Protocol for web scraping services."""
    async def scrape_url(self, url: str) -> Dict[str, Any]: ...


@runtime_checkable
class WhitelistServiceProtocol(Protocol):
    """Protocol for domain whitelisting and source tiers."""
    @classmethod
    def is_whitelisted_domain(cls, domain: str) -> bool: ...
    @classmethod
    def get_domain_tier(cls, domain: str) -> int: ...
    @classmethod
    def get_rss_feed_sources(cls) -> List[Dict[str, Any]]: ...


@runtime_checkable
class ScoringServiceProtocol(Protocol):
    """Protocol for story candidate scoring engines."""
    @staticmethod
    async def calculate_composite_score(
        session: AsyncSession,
        candidate: CandidateStory,
        weights: Optional[Dict[str, float]] = None,
        historical_bias_lookup: Optional[Dict[str, float]] = None,
    ) -> float: ...

    @staticmethod
    async def partition_portfolio(
        session: AsyncSession,
        candidates: List[Dict[str, Any]],
        target_size: int = 8,
    ) -> List[Dict[str, Any]]: ...
