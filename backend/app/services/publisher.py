import uuid
from typing import List, Tuple
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.services.url_validator import URLValidatorService

class PublicationGateService:
    @staticmethod
    def validate_edition_structure(edition: Edition) -> Tuple[bool, List[str]]:
        """
        Validates edition compliance against PRD Section 36 requirements:
        1. Minimum story requirements satisfied unless explicitly marked low-signal.
        2. Every story has headline (>= 5 chars).
        3. Every story has summary (>= 20 chars).
        4. Every story has 'Why It Matters' (>= 20 chars).
        5. Every story has at least one valid primary source URL.
        6. Exactly one lead story designated.
        7. No duplicate story slugs.
        8. Every story must have a published_at timestamp within the allowable lookback window.
        """
        errors = []
        stories = edition.stories or []

        if not stories:
            errors.append("Edition has zero stories staged.")
            return False, errors

        # Check story count
        if not edition.low_signal_notice and len(stories) < 5:
            errors.append(f"Requires at least 5 stories (found {len(stories)}) unless marked low_signal.")

        # Check lead story
        lead_stories = [s for s in stories if s.is_lead]
        if len(lead_stories) == 0:
            errors.append("No lead story designated.")
        elif len(lead_stories) > 1:
            errors.append(f"Multiple ({len(lead_stories)}) lead stories designated.")

        edition_dt = edition.date if isinstance(edition.date, date) else date.today()
        earliest_allowed = edition_dt - timedelta(days=2) # 48 hour lookback window

        # Story content validation
        seen_slugs = set()
        for idx, s in enumerate(stories):
            label = f"Story #{idx+1} ('{s.title[:30]}...')"
            if not s.title or len(s.title.strip()) < 5:
                errors.append(f"{label}: headline is too short (min 5 characters).")
            if not s.summary or len(s.summary.strip()) < 20:
                errors.append(f"{label}: summary is too short (min 20 characters).")
            if not s.why_it_matters or len(s.why_it_matters.strip()) < 20:
                errors.append(f"{label}: missing or insufficient 'Why It Matters' analysis (min 20 characters).")
            if not s.sources:
                errors.append(f"{label}: missing required primary source URL.")
            else:
                for src in s.sources:
                    if not src.url or not src.url.startswith("http"):
                        errors.append(f"{label}: invalid source URL '{src.url}'.")

            # Check story recency
            if s.published_at:
                s_date = s.published_at.date() if hasattr(s.published_at, "date") else None
                if s_date and s_date < earliest_allowed:
                    errors.append(
                        f"{label}: story is stale (published_at {s_date} is older than "
                        f"48-hour lookback window relative to edition date {edition_dt})."
                    )

            if s.slug in seen_slugs:
                errors.append(f"{label}: duplicate slug '{s.slug}'.")
            seen_slugs.add(s.slug)

        return len(errors) == 0, errors

    @staticmethod
    async def validate_edition_sources_http(edition: Edition) -> Tuple[bool, List[str]]:
        """Validates that all primary source URLs in the edition resolve with HTTP 200."""
        errors = []
        urls_to_check = []
        url_story_map = {}

        for idx, s in enumerate(edition.stories or []):
            label = f"Story #{idx+1} ('{s.title[:30]}...')"
            for src in s.sources or []:
                if src.url and src.url.startswith("http"):
                    urls_to_check.append(src.url)
                    url_story_map[src.url] = label

        if not urls_to_check:
            return True, []

        validation_results = await URLValidatorService.validate_urls_batch(urls_to_check)
        for url, res in validation_results.items():
            if not res["is_valid"]:
                label = url_story_map.get(url, "Story")
                errors.append(f"{label}: primary source URL '{url}' failed HTTP 200 validation (status: {res['status_code']}, error: {res['error']}).")

        return len(errors) == 0, errors

    @classmethod
    async def publish(cls, session: AsyncSession, edition_id: uuid.UUID) -> Tuple[bool, List[str], Edition]:
        res = await session.execute(
            select(Edition)
            .where(Edition.id == edition_id)
            .options(selectinload(Edition.stories).selectinload(Story.sources))
        )
        edition = res.scalar_one_or_none()
        if not edition:
            return False, [f"Edition {edition_id} not found"], None

        is_valid, errors = cls.validate_edition_structure(edition)
        if not is_valid:
            return False, errors, edition

        # Also validate HTTP 200 reachability of all primary source links
        sources_valid, source_errors = await cls.validate_edition_sources_http(edition)
        if not sources_valid:
            return False, source_errors, edition

        # Execute idempotent publication
        now = datetime.now(timezone.utc)
        edition.status = "published"
        edition.published_at = now
        for s in edition.stories:
            s.status = "published"
            if not s.published_at:
                s.published_at = now

        await session.commit()
        await session.refresh(edition)
        return True, [], edition
