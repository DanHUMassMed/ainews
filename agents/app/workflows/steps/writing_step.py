"""Writing synthesis step generating authoritative newspaper articles."""

import re
import html
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from email.utils import parsedate_to_datetime
from agents.app.agents.writing import synthesize_story


class WritingStep:
    """Synthesizes candidate stories into publication-grade briefing items."""

    def __init__(self, live: bool = False):
        self.live = live

    async def synthesize_candidate(self, c: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Synthesizes a publication-grade newspaper story using the Writing Agent with self-review."""
        pub_name = c.get('publisher', 'Frontier Lab')
        c_title = (c.get('title') or '').strip() or f"AI Architecture Update from {pub_name}"

        # Delegate directly to Writing Agent synthesis runner with self-review loop
        story_item = await synthesize_story(c, idx=idx, live=self.live)

        headline = story_item.get("headline") or story_item.get("title") or c_title
        summary = story_item.get("summary", "")
        why_it_matters = story_item.get("why_it_matters", "")
        body = story_item.get("body", "")

        # Clean any HTML entities/tags thoroughly
        headline = re.sub(r"<[^>]+>", "", html.unescape(headline)).strip()
        summary = re.sub(r"<[^>]+>", "", html.unescape(summary)).strip()
        why_it_matters = re.sub(r"<[^>]+>", "", html.unescape(why_it_matters)).strip()
        body = re.sub(r"<[^>]+>", "", html.unescape(body)).strip()

        clean_title = re.sub(r'[^\w\s-]', '', headline).strip().lower()
        slug = re.sub(r'[\s-]+', '-', clean_title)[:60] or f"story-{idx + 1}"

        pub_raw = c.get("published_at") or c.get("published_date")
        pub_at = None
        if pub_raw:
            try:
                dt = parsedate_to_datetime(pub_raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                pub_at = dt.astimezone(timezone.utc).isoformat()
            except Exception:
                try:
                    dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    pub_at = dt.astimezone(timezone.utc).isoformat()
                except Exception:
                    pass
        if not pub_at:
            pub_at = datetime.now(timezone.utc).isoformat()

        return {
            "title": headline,
            "slug": slug,
            "summary": summary,
            "why_it_matters": why_it_matters,
            "body": body,
            "image_url": c.get("image_url"),
            "is_lead": c.get("is_lead", (idx == 0)),
            "position": idx,
            "published_at": pub_at,
            "category_slugs": story_item.get("category_slugs") or c.get("category_slugs", ["ai-models"]),
            "sources": [{
                "url": c["url"],
                "title": headline,
                "publisher": pub_name,
                "published_at": pub_at,
            }],
        }

    async def execute(self, selected_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize candidate stories into publication-grade briefing items."""
        sem = asyncio.Semaphore(2)

        async def _synth(c, idx):
            async with sem:
                return await self.synthesize_candidate(c, idx)

        tasks = [_synth(c, idx) for idx, c in enumerate(selected_candidates)]
        stories = await asyncio.gather(*tasks)
        return list(stories)
