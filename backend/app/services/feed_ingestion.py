"""Production Feed Ingestion Service.

Authoritative service for ingesting whitelisted RSS, Atom, ArXiv, and Reddit feeds.
Extracts:
1. Canonical public article links (never .xml feed URLs).
2. Clean title, excerpt, and full content when available.
3. Hero image URLs (enclosure, media:content, inline img, or og:image fallback).
4. Standardized ISO timestamps and whitelist tier metadata.
"""

import re
import html
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
import httpx

from backend.app.services.whitelist import WhitelistService, WhitelistEntry
from backend.app.services.deduplication import DeduplicationService

logger = logging.getLogger("ainews.feed_ingestion")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 "
        "AI-Industry-News-Aggregator/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/rss+xml,*/*;q=0.8",
}

def clean_html(raw_html: str) -> str:
    """Strips HTML tags and unescapes text entities thoroughly."""
    if not raw_html:
        return ""
    # 1. Unpack CDATA
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", raw_html)
    # 2. Multi-pass unescape so &lt;p&gt; becomes <p> and &lt;img... becomes <img...
    text = html.unescape(text)
    text = html.unescape(text)
    # 3. Strip script and style blocks
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
    # 4. Strip all HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # 5. Final entity cleanup & normalize whitespace
    text = html.unescape(text)
    return " ".join(text.split()).strip()

class FeedIngestionService:
    @staticmethod
    def parse_datetime_to_iso(d_str: Optional[str]) -> Optional[str]:
        if not d_str:
            return None
        try:
            dt = parsedate_to_datetime(d_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            pass
        try:
            dt = datetime.fromisoformat(d_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return None
    @staticmethod
    def extract_image_url(item_xml: str, client_soup: Optional[str] = None) -> Optional[str]:
        """Extracts hero image URL from enclosure, media:content, or <img> tag."""
        # 1. Check enclosure tag
        enc_match = re.search(r'<enclosure[^>]*url=[\"\']([^\"\']+)[\"\']', item_xml, re.IGNORECASE)
        if enc_match:
            return enc_match.group(1).strip()

        # 2. Check media:content or media:thumbnail
        media_match = re.search(r'<(?:media:content|media:thumbnail)[^>]*url=[\"\']([^\"\']+)[\"\']', item_xml, re.IGNORECASE)
        if media_match:
            return media_match.group(1).strip()

        # 3. Check inline <img> src
        img_match = re.search(r'<img[^>]+src=[\"\']([^\"\']+)[\"\']', item_xml, re.IGNORECASE)
        if img_match:
            img_url = img_match.group(1).strip()
            # Ignore tiny tracking pixels
            if not any(px in img_url.lower() for px in ["track", "beacon", "pixel", "1x1", ".gif"]):
                return img_url

        return None

    @classmethod
    async def fetch_og_image(cls, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """Fallback to extract og:image from the canonical article page."""
        try:
            r = await client.get(url, headers=DEFAULT_HEADERS, timeout=6.0, follow_redirects=True)
            if r.status_code == 200:
                og_match = re.search(r'<meta[^>]+property=[\"\']og:image[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', r.text, re.IGNORECASE)
                if not og_match:
                    og_match = re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+property=[\"\']og:image[\"\']', r.text, re.IGNORECASE)
                if og_match:
                    return og_match.group(1).strip()
        except Exception:
            pass
        return None

    @classmethod
    def parse_rss_or_atom(cls, xml_text: str, source_entry: WhitelistEntry) -> List[Dict[str, Any]]:
        """Parses RSS 2.0 or Atom XML content into structured candidate leads."""
        items = []
        if not xml_text:
            return items

        # RSS 2.0: match <item>...</item>
        raw_items = re.findall(r'(<item[\s\S]*?</item>)', xml_text, re.IGNORECASE)
        is_atom = False
        if not raw_items:
            # Atom: match <entry>...</entry>
            raw_items = re.findall(r'(<entry[\s\S]*?</entry>)', xml_text, re.IGNORECASE)
            is_atom = True

        for raw_item in raw_items:
            try:
                # 1. Extract canonical URL
                canonical_url = ""
                if is_atom:
                    link_match = re.search(r'<link[^>]*rel=[\"\']alternate[\"\'][^>]*href=[\"\']([^\"\']+)[\"\']', raw_item, re.IGNORECASE)
                    if not link_match:
                        link_match = re.search(r'<link[^>]*href=[\"\']([^\"\']+)[\"\']', raw_item, re.IGNORECASE)
                    canonical_url = link_match.group(1).strip() if link_match else ""
                else:
                    link_match = re.search(r'<link[^>]*>(.*?)</link>', raw_item, re.IGNORECASE)
                    if link_match:
                        canonical_url = link_match.group(1).strip()
                    else:
                        guid_match = re.search(r'<guid[^>]*>(https?://[^\s<]+)</guid>', raw_item, re.IGNORECASE)
                        if guid_match:
                            canonical_url = guid_match.group(1).strip()

                if not canonical_url or not canonical_url.startswith("http"):
                    continue

                # 2. Extract Title
                title_match = re.search(r'<title[^>]*>([\s\S]*?)</title>', raw_item, re.IGNORECASE)
                title = clean_html(title_match.group(1)) if title_match else "Untitled AI Announcement"

                # 3. Extract Summary / Content
                desc_match = (
                    re.search(r'<content:encoded[^>]*>([\s\S]*?)</content:encoded>', raw_item, re.IGNORECASE) or
                    re.search(r'<content[^>]*>([\s\S]*?)</content>', raw_item, re.IGNORECASE) or
                    re.search(r'<description[^>]*>([\s\S]*?)</description>', raw_item, re.IGNORECASE) or
                    re.search(r'<summary[^>]*>([\s\S]*?)</summary>', raw_item, re.IGNORECASE)
                )
                raw_content = desc_match.group(1) if desc_match else ""
                text_snippet = clean_html(raw_content)
                if len(text_snippet) > 600:
                    text_snippet = text_snippet[:600] + "..."

                # 4. Extract Hero Image
                image_url = cls.extract_image_url(raw_item)

                # 5. Extract Publication Date
                date_match = (
                    re.search(r'<pubDate[^>]*>(.*?)</pubDate>', raw_item, re.IGNORECASE) or
                    re.search(r'<published[^>]*>(.*?)</published>', raw_item, re.IGNORECASE) or
                    re.search(r'<updated[^>]*>(.*?)</updated>', raw_item, re.IGNORECASE)
                )
                pub_str = date_match.group(1).strip() if date_match else None
                pub_iso = cls.parse_datetime_to_iso(pub_str)

                items.append({
                    "url": DeduplicationService.normalize_url(canonical_url),
                    "raw_url": canonical_url,
                    "title": title,
                    "snippet": text_snippet,
                    "content": clean_html(raw_content),
                    "image_url": image_url,
                    "publisher": source_entry.domain,
                    "tier": source_entry.tier,
                    "category": source_entry.category,
                    "published_date": pub_iso,
                    "published_at": pub_iso,
                    "source_type": "rss_feed",
                    "ingestion_strategy": source_entry.ingestion_strategy,
                })
            except Exception as e:
                logger.debug(f"Error parsing item: {e}")

        return items

    @classmethod
    async def fetch_single_feed(cls, entry: WhitelistEntry, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Fetches and parses a single whitelist feed endpoint."""
        feed_url = entry.active_feed or entry.recommended_endpoint
        if not feed_url or not feed_url.startswith("http"):
            return []

        try:
            r = await client.get(feed_url, headers=DEFAULT_HEADERS, timeout=10.0, follow_redirects=True)
            if r.status_code != 200:
                logger.warning(f"Feed fetch failed ({r.status_code}) for {feed_url}")
                return []
            leads = cls.parse_rss_or_atom(r.text, entry)
            return leads
        except Exception as e:
            logger.debug(f"Exception fetching feed {feed_url}: {e}")
            return []

    @classmethod
    async def ingest_whitelisted_feeds(
        cls,
        max_items_per_feed: int = 5,
        target_sources: Optional[List[WhitelistEntry]] = None
    ) -> List[Dict[str, Any]]:
        """Concurrently ingests all active whitelisted RSS/Atom feeds."""
        sources = target_sources or WhitelistService.get_rss_feed_sources()
        if not sources:
            logger.warning("No whitelisted RSS sources available for ingestion.")
            return []

        semaphore = asyncio.Semaphore(10)
        all_leads = []
        seen_urls = set()

        async with httpx.AsyncClient(timeout=12.0) as client:
            async def sem_fetch(src: WhitelistEntry):
                async with semaphore:
                    return await cls.fetch_single_feed(src, client)

            tasks = [sem_fetch(src) for src in sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    for item in res[:max_items_per_feed]:
                        norm_url = item["url"]
                        if norm_url not in seen_urls:
                            seen_urls.add(norm_url)
                            all_leads.append(item)

        logger.info(f"Ingested {len(all_leads)} deduplicated candidates from {len(sources)} whitelisted feeds")
        return all_leads

    @classmethod
    async def ingest_arxiv_preprints(
        cls,
        categories: str = "cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG",
        max_results: int = 15
    ) -> List[Dict[str, Any]]:
        """Queries structured ArXiv API with explicit category filter."""
        api_url = f"http://export.arxiv.org/api/query?search_query={categories}&max_results={max_results}&sortBy=submittedDate"
        dummy_entry = WhitelistEntry(
            url_path="arxiv.org",
            tier="Tier 4",
            category="Preprints",
            ingestion_strategy="api_query",
        )
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                r = await client.get(api_url, headers=DEFAULT_HEADERS)
                if r.status_code == 200:
                    leads = cls.parse_rss_or_atom(r.text, dummy_entry)
                    for lead in leads:
                        lead["source_type"] = "arxiv_api"
                        lead["publisher"] = "arxiv.org"
                    return leads
        except Exception as e:
            logger.warning(f"Error querying ArXiv API: {e}")
        return []

    @classmethod
    async def ingest_reddit_pulse(
        cls,
        subreddit: str = "LocalLLaMA",
        min_score: int = 100,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """Queries Reddit JSON endpoint with upvote threshold filter."""
        url = f"https://www.reddit.com/r/{subreddit}/top.json?t=day&limit={limit}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        leads = []
        try:
            async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    data = r.json()
                    children = data.get("data", {}).get("children", [])
                    for post in children:
                        pdata = post.get("data", {})
                        score = pdata.get("score", 0)
                        if score < min_score:
                            continue
                        permalink = f"https://www.reddit.com{pdata.get('permalink', '')}"
                        outbound_url = pdata.get("url", permalink)
                        title = pdata.get("title", "")
                        selftext = pdata.get("selftext", "")

                        leads.append({
                            "url": DeduplicationService.normalize_url(outbound_url),
                            "raw_url": outbound_url,
                            "reddit_permalink": permalink,
                            "title": f"[{subreddit}] {title}",
                            "snippet": selftext[:400] if selftext else f"Community discussion with {score} upvotes.",
                            "publisher": "reddit.com",
                            "tier": "Tier 4",
                            "category": "Community / Open Weights",
                            "score": score,
                            "source_type": "reddit_community",
                            "ingestion_strategy": "json_filtered",
                        })
        except Exception as e:
            logger.warning(f"Error fetching Reddit pulse for r/{subreddit}: {e}")
        return leads
