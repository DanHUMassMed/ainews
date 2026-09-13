import logging
from typing import List, Dict, Any, Optional
import httpx
from backend.app.core.config import settings
from backend.app.services.deduplication import DeduplicationService

logger = logging.getLogger("ainews.searxng")

DEFAULT_DISCOVERY_QUERIES = [
    "AI compute inference datacenter architecture infrastructure hardware",
    "open weights model release weights HuggingFace open source LLM",
    "custom silicon AI accelerator NPU GPU Blackwell wafer scale",
    "autonomous coding agent runtime tooling protocol framework",
    "AI research paper benchmark reasoning architecture arxiv",
]

class SearXNGClient:
    def __init__(self, base_url: str = settings.SEARXNG_URL):
        self.base_url = base_url.rstrip("/")

    async def search(
        self,
        query: str,
        time_range: str = "day", # day, week, month
        max_results: int = 40,
        categories: str = "general,it,science",
    ) -> List[Dict[str, Any]]:
        params = {
            "q": query,
            "format": "json",
            "time_range": time_range,
            "categories": categories,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.base_url}/search", params=params)
                if resp.status_code != 200:
                    logger.error(f"SearXNG query failed with status {resp.status_code}: {resp.text}")
                    return []
                data = resp.json()
                results = data.get("results", [])
                
                clean_items = []
                for r in results[:max_results]:
                    url = r.get("url", "").strip()
                    title = r.get("title", "").strip()
                    content = r.get("content", "").strip()
                    if not url or not title:
                        continue
                    clean_items.append({
                        "url": DeduplicationService.normalize_url(url),
                        "raw_url": url,
                        "title": title,
                        "snippet": content,
                        "engine": r.get("engine", "searxng"),
                        "published_date": r.get("publishedDate"),
                    })
                return clean_items
        except Exception as e:
            logger.error(f"SearXNG connection error on query '{query}': {e}")
            return []

    async def run_discovery_matrix(
        self,
        queries: Optional[List[str]] = None,
        time_range: str = "day",
    ) -> List[Dict[str, Any]]:
        target_queries = queries or DEFAULT_DISCOVERY_QUERIES
        all_candidates = []
        seen_urls = set()

        for q in target_queries:
            results = await self.search(q, time_range=time_range)
            for item in results:
                norm_url = item["url"]
                if norm_url not in seen_urls:
                    seen_urls.add(norm_url)
                    all_candidates.append(item)

        return all_candidates
