"""Production Whitelist Service.

Authoritative source of vetted publication domains, feed endpoints,
and tier configurations for Hermes AI News pipeline.
Loads exclusively from backend/app/data/whitelist.csv (zero evaluation/ dependencies).
"""

import os
import csv
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field

logger = logging.getLogger("ainews.whitelist")

DEFAULT_WHITELIST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "whitelist.csv")
)

class WhitelistEntry(BaseModel):
    url_path: str
    tier: str
    category: str
    status_code: int = 200
    challenge_type: str = "None"
    is_blocked: bool = False
    is_paywall: bool = False
    active_feed: Optional[str] = None
    searx_count: int = 0
    ingestion_strategy: str = "direct_scrape"
    recommended_endpoint: str = ""
    pipeline_action: str = ""
    scoping_advice: str = ""
    domain: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if not self.domain:
            self.domain = self.url_path.split("/")[0].lower()

class WhitelistService:
    _entries: Optional[List[WhitelistEntry]] = None
    _domain_map: Optional[Dict[str, WhitelistEntry]] = None

    @classmethod
    def load(cls, file_path: Optional[str] = None, force_reload: bool = False) -> List[WhitelistEntry]:
        """Loads and caches the production whitelist CSV."""
        if cls._entries is not None and not force_reload:
            return cls._entries

        path = file_path or DEFAULT_WHITELIST_PATH
        if not os.path.exists(path):
            logger.warning(f"Production whitelist CSV not found at {path}")
            cls._entries = []
            cls._domain_map = {}
            return []

        entries = []
        domain_map = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url_p = row.get("url_path", "").strip()
                if not url_p:
                    continue
                try:
                    feed_val = row.get("active_feed", "").strip()
                    if feed_val in ("", "None"):
                        feed_val = None

                    entry = WhitelistEntry(
                        url_path=url_p,
                        tier=row.get("tier", "Tier 3").strip(),
                        category=row.get("category", "General AI").strip(),
                        status_code=int(row.get("status_code", 200) or 200),
                        challenge_type=row.get("challenge_type", "None").strip(),
                        is_blocked=str(row.get("is_blocked", "False")).lower() in ("true", "1"),
                        is_paywall=str(row.get("is_paywall", "False")).lower() in ("true", "1"),
                        active_feed=feed_val,
                        searx_count=int(row.get("searx_count", 0) or 0),
                        ingestion_strategy=row.get("ingestion_strategy", "direct_scrape").strip(),
                        recommended_endpoint=row.get("recommended_endpoint", "").strip(),
                        pipeline_action=row.get("pipeline_action", "").strip(),
                        scoping_advice=row.get("scoping_advice", "").strip(),
                    )
                    entries.append(entry)
                    domain_map[entry.domain] = entry
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning("Error parsing whitelist entry %s: %s (type=%s)", url_p, e, type(e).__name__)

        cls._entries = entries
        cls._domain_map = domain_map
        logger.info(f"Loaded {len(entries)} verified entries into WhitelistService")
        return entries

    @classmethod
    def get_all_sources(cls) -> List[WhitelistEntry]:
        return cls.load()

    @classmethod
    def get_rss_feed_sources(cls) -> List[WhitelistEntry]:
        """Returns all sources configured for RSS/Atom feed ingestion."""
        return [e for e in cls.load() if e.active_feed and e.ingestion_strategy in ("rss_feed", "firecrawl_or_feed")]

    @classmethod
    def get_api_sources(cls) -> List[WhitelistEntry]:
        """Returns sources configured for structured API query (ArXiv, Reddit, OpenReview)."""
        return [e for e in cls.load() if e.ingestion_strategy in ("api_query", "json_filtered")]

    @classmethod
    def get_secondary_discovery_sources(cls) -> List[WhitelistEntry]:
        """Returns paywalled scoop/business sources configured for secondary discovery only."""
        return [e for e in cls.load() if e.ingestion_strategy == "secondary_discovery_only"]

    @classmethod
    def extract_domain(cls, url: str) -> str:
        """Extracts normalized hostname from a URL string."""
        from backend.app.utils.urls import extract_domain
        return extract_domain(url)

    @classmethod
    def get_source_for_url(cls, url: str) -> Optional[WhitelistEntry]:
        """Finds matching WhitelistEntry for a given article URL."""
        domain = cls.extract_domain(url)
        cls.load()
        if not domain or not cls._domain_map:
            return None
        # Exact domain match
        if domain in cls._domain_map:
            return cls._domain_map[domain]
        # Subdomain check (e.g. blogs.nvidia.com vs nvidia.com)
        for d, entry in cls._domain_map.items():
            if domain.endswith(f".{d}") or d.endswith(f".{domain}"):
                return entry
        return None

    @classmethod
    def is_whitelisted_domain(cls, url: str) -> bool:
        """Checks if a URL belongs to a whitelisted domain."""
        return cls.get_source_for_url(url) is not None
