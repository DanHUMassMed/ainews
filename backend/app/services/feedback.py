import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, desc
from sqlalchemy.orm import selectinload
from backend.app.models.feedback import Feedback
from backend.app.models.story import Story
from backend.app.models.category import Category, story_categories
from backend.app.models.configuration import EditorialConfiguration
from backend.app.schemas.feedback import FeedbackAnalyticsResponse, CategoryFeedbackItem

class FeedbackService:
    @staticmethod
    async def get_story_votes(session: AsyncSession, story_id: uuid.UUID) -> Tuple[int, int]:
        """Returns (upvotes, downvotes) for a story in a single aggregated query."""
        stmt = select(
            func.coalesce(func.sum(case((Feedback.vote == 1, 1), else_=0)), 0),
            func.coalesce(func.sum(case((Feedback.vote == -1, 1), else_=0)), 0),
        ).where(Feedback.story_id == story_id)
        res = await session.execute(stmt)
        row = res.fetchone()
        if not row:
            return (0, 0)
        return int(row[0] or 0), int(row[1] or 0)

    @staticmethod
    async def get_stories_votes_batch(session: AsyncSession, story_ids: List[uuid.UUID]) -> Dict[uuid.UUID, Tuple[int, int]]:
        """Returns mapping of story_id -> (upvotes, downvotes) in a single batch query."""
        if not story_ids:
            return {}
        stmt = (
            select(
                Feedback.story_id,
                func.coalesce(func.sum(case((Feedback.vote == 1, 1), else_=0)), 0),
                func.coalesce(func.sum(case((Feedback.vote == -1, 1), else_=0)), 0),
            )
            .where(Feedback.story_id.in_(story_ids))
            .group_by(Feedback.story_id)
        )
        res = await session.execute(stmt)
        mapping = {s_id: (0, 0) for s_id in story_ids}
        for row in res.fetchall():
            s_id, up, dn = row
            mapping[s_id] = (int(up or 0), int(dn or 0))
        return mapping

    @staticmethod
    async def is_cold_start_active(session: AsyncSession) -> bool:
        # Check configuration
        cfg_res = await session.execute(
            select(EditorialConfiguration).where(EditorialConfiguration.key == "cold_start")
        )
        cfg = cfg_res.scalar_one_or_none()
        min_votes = 100
        if cfg and isinstance(cfg.value, dict):
            min_votes = int(cfg.value.get("min_feedback_votes", 100))

        # Check total votes in database
        total_res = await session.execute(select(func.count(Feedback.id)))
        total_votes = total_res.scalar() or 0
        return total_votes < min_votes

    @staticmethod
    async def record_vote(session: AsyncSession, story_id: uuid.UUID, vote: int, session_id: str) -> Dict[str, Any]:
        # Validate story exists
        story_res = await session.execute(select(Story).where(Story.id == story_id))
        story = story_res.scalar_one_or_none()
        if not story:
            raise ValueError(f"Story {story_id} not found")

        # Clamp vote to +1 or -1
        clean_vote = 1 if vote > 0 else -1

        # Check existing vote by session
        existing_res = await session.execute(
            select(Feedback).where(
                and_(Feedback.story_id == story_id, Feedback.session_id == session_id)
            )
        )
        existing = existing_res.scalar_one_or_none()
        if existing:
            existing.vote = clean_vote
            existing.created_at = datetime.now(timezone.utc)
        else:
            fb = Feedback(
                story_id=story_id,
                vote=clean_vote,
                session_id=session_id,
                created_at=datetime.now(timezone.utc),
            )
            session.add(fb)

        await session.commit()

        # Return updated counts
        up_res = await session.execute(
            select(func.count(Feedback.id)).where(
                and_(Feedback.story_id == story_id, Feedback.vote == 1)
            )
        )
        down_res = await session.execute(
            select(func.count(Feedback.id)).where(
                and_(Feedback.story_id == story_id, Feedback.vote == -1)
            )
        )
        return {
            "status": "recorded",
            "story_id": story_id,
            "vote": clean_vote,
            "upvotes": up_res.scalar() or 0,
            "downvotes": down_res.scalar() or 0,
        }

    @staticmethod
    async def update_vote(session: AsyncSession, feedback_id: uuid.UUID, new_vote: int) -> Dict[str, Any]:
        stmt = select(Feedback).where(Feedback.id == feedback_id)
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            raise ValueError(f"Feedback vote {feedback_id} not found")

        clean_vote = 1 if new_vote > 0 else -1
        record.vote = clean_vote
        record.created_at = datetime.now(timezone.utc)
        await session.commit()
        return {
            "status": "updated",
            "id": str(record.id),
            "story_id": str(record.story_id),
            "vote": clean_vote,
        }

    @staticmethod
    async def delete_vote(session: AsyncSession, feedback_id: uuid.UUID) -> Dict[str, Any]:
        stmt = select(Feedback).where(Feedback.id == feedback_id)
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            raise ValueError(f"Feedback vote {feedback_id} not found")

        await session.delete(record)
        await session.commit()
        return {"status": "deleted", "id": str(feedback_id)}

    @staticmethod
    async def get_category_overrides(session: AsyncSession) -> Dict[str, Any]:
        cfg_res = await session.execute(
            select(EditorialConfiguration).where(EditorialConfiguration.key == "category_bias_overrides")
        )
        cfg = cfg_res.scalar_one_or_none()
        if cfg and isinstance(cfg.value, dict):
            return cfg.value
        return {}

    @staticmethod
    async def set_category_override(
        session: AsyncSession,
        slug: str,
        manual_bias: float,
        active: bool = True,
        reason: Optional[str] = "",
    ) -> Dict[str, Any]:
        cfg_res = await session.execute(
            select(EditorialConfiguration).where(EditorialConfiguration.key == "category_bias_overrides")
        )
        cfg = cfg_res.scalar_one_or_none()
        clean_bias = round(max(-3.0, min(3.0, float(manual_bias))), 2)

        overrides = {}
        if cfg and isinstance(cfg.value, dict):
            overrides = dict(cfg.value)

        overrides[slug] = {
            "manual_bias": clean_bias,
            "active": bool(active),
            "reason": str(reason or "").strip(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if cfg:
            cfg.value = overrides
            cfg.updated_at = datetime.now(timezone.utc)
        else:
            cfg = EditorialConfiguration(
                key="category_bias_overrides",
                value=overrides,
                description="Manual editorial category bias overrides",
                updated_at=datetime.now(timezone.utc),
            )
            session.add(cfg)

        await session.commit()
        return overrides

    @staticmethod
    async def delete_category_override(session: AsyncSession, slug: str) -> Dict[str, Any]:
        cfg_res = await session.execute(
            select(EditorialConfiguration).where(EditorialConfiguration.key == "category_bias_overrides")
        )
        cfg = cfg_res.scalar_one_or_none()
        if not cfg or not isinstance(cfg.value, dict):
            return {}

        overrides = dict(cfg.value)
        if slug in overrides:
            del overrides[slug]
            cfg.value = overrides
            cfg.updated_at = datetime.now(timezone.utc)
            await session.commit()
        return overrides

    @classmethod
    async def get_history(cls, session: AsyncSession, limit: int = 50, days: int = 30) -> List[Dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(Feedback)
            .where(Feedback.created_at >= cutoff)
            .order_by(desc(Feedback.created_at))
            .limit(limit)
            .options(selectinload(Feedback.story).selectinload(Story.categories))
        )
        res = await session.execute(stmt)
        records = []
        for f in res.scalars().all():
            records.append({
                "id": str(f.id),
                "story_id": str(f.story_id),
                "story_title": f.story.title if f.story else "Untitled Story",
                "story_slug": f.story.slug if f.story else None,
                "vote": f.vote,
                "session_id": f.session_id,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "categories": [
                    {"name": c.name, "slug": c.slug} for c in f.story.categories
                ] if f.story else [],
            })
        return records

    @classmethod
    async def get_analytics(cls, session: AsyncSession, window_days: int = 30) -> FeedbackAnalyticsResponse:
        cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
        cold_start = await cls.is_cold_start_active(session)
        overrides = await cls.get_category_overrides(session)

        # Total votes in window
        case_up = case((Feedback.vote == 1, 1), else_=0)
        case_dn = case((Feedback.vote == -1, 1), else_=0)
        tot_res = await session.execute(
            select(
                func.count(Feedback.id),
                func.coalesce(func.sum(case_up), 0),
                func.coalesce(func.sum(case_dn), 0),
            ).where(Feedback.created_at >= cutoff)
        )
        tot_row = tot_res.fetchone()
        total_votes = tot_row[0] or 0
        total_up = tot_row[1] or 0
        total_dn = tot_row[2] or 0
        approval_rate = round(total_up / total_votes, 3) if total_votes > 0 else 0.50

        # Outer join to include ALL taxonomy categories regardless of vote count
        cat_query = (
            select(
                Category.name,
                Category.slug,
                func.coalesce(func.sum(case((and_(Feedback.vote == 1, Feedback.created_at >= cutoff), 1), else_=0)), 0).label("up"),
                func.coalesce(func.sum(case((and_(Feedback.vote == -1, Feedback.created_at >= cutoff), 1), else_=0)), 0).label("down"),
            )
            .select_from(Category)
            .outerjoin(story_categories, story_categories.c.category_id == Category.id)
            .outerjoin(Story, Story.id == story_categories.c.story_id)
            .outerjoin(Feedback, and_(Feedback.story_id == Story.id, Feedback.created_at >= cutoff))
            .group_by(Category.name, Category.slug)
            .order_by(Category.name.asc())
        )
        cat_res = await session.execute(cat_query)
        categories = []
        positive_topics = []
        negative_topics = []

        for row in cat_res.fetchall():
            c_name, c_slug, c_up, c_dn = row
            c_up = int(c_up or 0)
            c_dn = int(c_dn or 0)
            c_tot = c_up + c_dn
            c_rate = round(c_up / c_tot, 3) if c_tot > 0 else 0.50
            raw_bias = round(max(-3.0, min(3.0, 6.0 * (c_rate - 0.50))), 2) if c_tot > 0 else 0.0

            # Editorial override resolution
            override_entry = overrides.get(c_slug)
            is_overridden = False
            override_bias_val = None
            override_reason_val = None
            effective_bias = raw_bias

            if isinstance(override_entry, dict) and override_entry.get("active", False):
                is_overridden = True
                override_bias_val = float(override_entry.get("manual_bias", 0.0))
                override_reason_val = str(override_entry.get("reason", ""))
                effective_bias = override_bias_val

            categories.append(
                CategoryFeedbackItem(
                    category_name=c_name,
                    slug=c_slug,
                    upvotes=c_up,
                    downvotes=c_dn,
                    total_votes=c_tot,
                    approval_rate=c_rate,
                    raw_bias=raw_bias,
                    override_active=is_overridden,
                    override_bias=override_bias_val,
                    effective_bias=effective_bias,
                    override_reason=override_reason_val,
                )
            )

            # Topics identification
            if effective_bias >= 1.0 or (c_rate >= 0.70 and c_tot >= 3):
                positive_topics.append(c_name)
            elif effective_bias <= -1.0 or (c_rate <= 0.35 and c_tot >= 3):
                negative_topics.append(c_name)

        return FeedbackAnalyticsResponse(
            window_days=window_days,
            total_votes=total_votes,
            total_upvotes=total_up,
            total_downvotes=total_dn,
            overall_approval_rate=approval_rate,
            cold_start_active=cold_start,
            categories=categories,
            top_positive_topics=positive_topics,
            top_negative_topics=negative_topics,
            category_overrides=overrides,
        )
