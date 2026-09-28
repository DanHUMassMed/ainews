"""URL utilities for domain extraction and URL normalization."""

from urllib.parse import urlparse, urlunparse
from typing import Optional


def extract_domain(url: Optional[str], default: str = "") -> str:
    """Extracts normalized hostname/domain from a URL string."""
    if not url:
        return default
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host or default
    except Exception:
        return default


def normalize_url(url: Optional[str]) -> str:
    """Strips marketing tracking parameters (utm_*, ref, etc.) and fragments."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]

    # Remove common tracking params
    query_parts = []
    if parsed.query:
        for param in parsed.query.split("&"):
            k = param.split("=")[0].lower()
            if not (k.startswith("utm_") or k in ("ref", "source", "fbclid", "gclid", "t", "spm")):
                query_parts.append(param)

    new_query = "&".join(query_parts)
    path = parsed.path.rstrip("/")
    return urlunparse((parsed.scheme.lower(), netloc, path, "", new_query, ""))
