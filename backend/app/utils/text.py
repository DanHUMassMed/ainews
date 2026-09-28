"""Text sanitization, slugification, and prohibited words list."""

import html
import re
from typing import List, Optional

PROHIBITED_BUZZWORDS: List[str] = [
    "game-changer", "revolutionary", "groundbreaking",
    "unprecedented", "paradigm shift", "skyrocketed",
    "unleash", "stunning", "next-gen"
]


def slugify(text: str, max_length: int = 100) -> str:
    """Creates a URL-safe slug from input text."""
    if not text:
        return ""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
    return re.sub(r'[\s-]+', '-', slug).strip('-')[:max_length]


def strip_html(v: Optional[str]) -> str:
    """Strips CDATA, script/style tags, HTML tags, and unescapes entities."""
    if not v or not isinstance(v, str):
        return ""
    # 1. Unpack CDATA
    t = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", v)
    # 2. Multi-pass unescape
    t = html.unescape(t)
    t = html.unescape(t)
    # 3. Strip script & style
    t = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", t, flags=re.IGNORECASE)
    t = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", t, flags=re.IGNORECASE)
    # 4. Strip tags
    t = re.sub(r"<[^>]+>", " ", t)
    # 5. Final entity cleanup
    t = html.unescape(t)
    return " ".join(t.split()).strip()
