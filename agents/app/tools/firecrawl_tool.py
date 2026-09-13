"""ADK Tool for Firecrawl Clean Markdown Web Scraping."""

from typing import Optional, List, Dict, Any
from backend.app.services.firecrawl import FirecrawlClient
from agents.app.config import FIRECRAWL_URL

_client = FirecrawlClient(base_url=FIRECRAWL_URL)

async def scrape_webpage(
    url: str,
    only_main_content: bool = True
) -> Dict[str, Any]:
    """Scrape a webpage and return clean, LLM-ready markdown content and metadata.

    Args:
        url: The HTTP/HTTPS URL of the article or document to scrape.
        only_main_content: If True, strips headers, footers, navigation, and ads.

    Returns:
        Dictionary containing markdown, title, description, and source metadata.
    """
    return await _client.scrape_url(url=url, formats=["markdown"], only_main_content=only_main_content)
