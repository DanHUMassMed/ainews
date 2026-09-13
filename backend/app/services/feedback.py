import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from backend.app.models.feedback import Feedback
from backend.app.models.story import Story
from backend.app.models.category import Category, story_categories
from backend.app.models.configuration import EditorialConfiguration
from backend.app.schemas.feedback import FeedbackAnalyticsResponse, CategoryFeedbackItem

class FeedbackService:
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

    @classmethod
    async def get_analytics(cls, session: AsyncSession, window_days: int = 30) -> FeedbackAnalyticsResponse:
        cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
        cold_start = await cls.is_cold_start_active(session)

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

        # Category breakdown
        cat_query = (
            select(
                Category.name,
                Category.slug,
                func.coalesce(func.sum(case_up), 0).label("up"),
                func.coalesce(func.sum(case_dn), 0).label("down"),
            )
            .select_from(Category)
            .join(story_categories, story_categories.c.category_id == Category.id)
            .join(Story, Story.id == story_categories.c.story_id)
            .join(Feedback, Feedback.story_id == Story.id)
            .where(Feedback.created_at >= cutoff)
            .group_by(Category.name, Category.slug)
        )
        cat_res = await session.execute(cat_query)
        categories = []
        positive_topics = []
        negative_topics = []

        for row in cat_res.fetchall():
            c_name, c_slug, c_up, c_dn = row
            c_up = c_up or 0
            c_dn = c_dn or 0
            c_tot = c_up + c_dn
            c_rate = round(c_up / c_tot, 3) if c_tot > 0 else 0.5
            categories.append(
                CategoryFeedbackItem(
                    category_name=c_name,
                    slug=c_slug,
                    upvotes=c_up,
                    downvotes=c_dn,
                    approval_rate=c_rate,
                )
            )
            if c_rate >= 0.70 and c_tot >= 3:
                positive_topics.append(c_name)
            elif c_rate <= 0.35 and c_tot >= 3:
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
        )
