"""FastAPI dependencies and service providers."""

from functools import lru_cache
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.services.searxng import SearXNGClient
from backend.app.services.firecrawl import FirecrawlClient
from backend.app.services.whitelist import WhitelistService
from backend.app.services.scoring import ScoringEngine
from backend.app.services.protocols import (
    SearchService,
    ScraperService,
    WhitelistServiceProtocol,
    ScoringServiceProtocol,
)


@lru_cache()
def get_searxng_client() -> SearchService:
    return SearXNGClient()


@lru_cache()
def get_firecrawl_client() -> ScraperService:
    return FirecrawlClient()


def get_whitelist_service() -> WhitelistServiceProtocol:
    return WhitelistService


def get_scoring_engine() -> ScoringServiceProtocol:
    return ScoringEngine
