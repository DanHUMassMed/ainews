import logging
from typing import Dict, Any, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger("ainews.firecrawl")

class FirecrawlClient:
    def __init__(self, base_url: str = settings.FIRECRAWL_URL):
        self.base_url = base_url.rstrip("/")

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Converts discovered URL to clean Markdown using local Firecrawl service.
        """
        if not url:
            return {"success": False, "error": "Empty URL"}

        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(f"{self.base_url}/v1/scrape", json=payload)
                if resp.status_code != 200:
                    logger.warning(f"Firecrawl scrape failed ({resp.status_code}) for {url}")
                    return {
                        "success": False,
                        "status_code": resp.status_code,
                        "error": resp.text[:200],
                        "markdown": "",
                    }

                data = resp.json()
                if data.get("success"):
                    scrape_data = data.get("data", {})
                    markdown = scrape_data.get("markdown", "")
                    metadata = scrape_data.get("metadata", {})
                    return {
                        "success": True,
                        "url": url,
                        "markdown": markdown,
                        "title": metadata.get("title", ""),
                        "description": metadata.get("description", ""),
                        "status_code": metadata.get("statusCode", 200),
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("error", "Unknown extraction error"),
                        "markdown": "",
                    }
        except Exception as e:
            logger.error(f"Firecrawl exception for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "markdown": "",
            }
