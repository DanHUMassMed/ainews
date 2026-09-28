"""Backend shared utilities package."""

from backend.app.utils.urls import extract_domain, normalize_url
from backend.app.utils.dates import parse_datetime_flexible
from backend.app.utils.text import slugify, strip_html, PROHIBITED_BUZZWORDS

__all__ = [
    "extract_domain",
    "normalize_url",
    "parse_datetime_flexible",
    "slugify",
    "strip_html",
    "PROHIBITED_BUZZWORDS",
]
