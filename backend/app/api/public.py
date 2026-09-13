import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.models.source import Source
from backend.app.models.category import Category, story_categories
from backend.app.models.feedback import Feedback
from backend.app.schemas.edition import EditionResponse, EditionDetailResponse
from backend.app.schemas.story import StoryResponse
from backend.app.schemas.category import CategoryResponse
from backend.app.schemas.feedback import FeedbackSubmitRequest, FeedbackResponse
from backend.app.services.feedback import FeedbackService

router = APIRouter(prefix="/public", tags=["Public Reader API"])

async def build_story_response(story: Story, session: AsyncSession) -> StoryResponse:
    up_res = await session.execute(
        select(func.count(Feedback.id)).where(and_(Feedback.story_id == story.id, Feedback.vote == 1))
    )
    dn_res = await session.execute(
        select(func.count(Feedback.id)).where(and_(Feedback.story_id == story.id, Feedback.vote == -1))
    )
    return StoryResponse(
        id=story.id,
        edition_id=story.edition_id,
        slug=story.slug,
        title=story.title,
        summary=story.summary,
        body=story.body,
        why_it_matters=story.why_it_matters,
        image_url=story.image_url,
        status=story.status,
        is_lead=story.is_lead,
        position=story.position,
        upvotes=up_res.scalar() or 0,
        downvotes=dn_res.scalar() or 0,
        created_at=story.created_at,
        updated_at=story.updated_at,
        published_at=story.published_at,
        sources=story.sources,
        categories=story.categories,
    )

@router.get("/editions/today", response_model=EditionDetailResponse)
async def get_today_edition(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Edition)
        .where(and_(Edition.status == "published", Edition.date <= date.today()))
        .order_by(Edition.date.desc())
        .limit(1)
        .options(
            selectinload(Edition.stories).selectinload(Story.sources),
            selectinload(Edition.stories).selectinload(Story.categories),
        )
    )
    res = await db.execute(stmt)
    edition = res.scalar_one_or_none()
    if not edition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No published edition found")

    story_responses = []
    lead_story_resp = None
    for s in edition.stories:
        sr = await build_story_response(s, db)
        story_responses.append(sr)
        if s.is_lead:
            lead_story_resp = sr

    return EditionDetailResponse(
        id=edition.id,
        date=edition.date,
        title=edition.title,
        introduction=edition.introduction,
        status=edition.status,
        low_signal_notice=edition.low_signal_notice,
        created_at=edition.created_at,
        updated_at=edition.updated_at,
        published_at=edition.published_at,
        story_count=len(edition.stories),
        stories=story_responses,
        lead_story=lead_story_resp,
    )

@router.get("/editions/{edition_date}", response_model=EditionDetailResponse)
async def get_edition_by_date(edition_date: date, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Edition)
        .where(Edition.date == edition_date, Edition.status == "published")
        .options(
            selectinload(Edition.stories).selectinload(Story.sources),
            selectinload(Edition.stories).selectinload(Story.categories),
        )
    )
    res = await db.execute(stmt)
    edition = res.scalar_one_or_none()
    if not edition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No edition found for date {edition_date}")

    story_responses = []
    lead_story_resp = None
    for s in edition.stories:
        sr = await build_story_response(s, db)
        story_responses.append(sr)
        if s.is_lead:
            lead_story_resp = sr

    return EditionDetailResponse(
        id=edition.id,
        date=edition.date,
        title=edition.title,
        introduction=edition.introduction,
        status=edition.status,
        low_signal_notice=edition.low_signal_notice,
        created_at=edition.created_at,
        updated_at=edition.updated_at,
        published_at=edition.published_at,
        story_count=len(edition.stories),
        stories=story_responses,
        lead_story=lead_story_resp,
    )

@router.get("/editions", response_model=List[EditionResponse])
async def list_editions(skip: int = 0, limit: int = 30, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Edition)
        .where(Edition.status == "published")
        .order_by(Edition.date.desc())
        .offset(skip)
        .limit(limit)
        .options(selectinload(Edition.stories))
    )
    res = await db.execute(stmt)
    editions = res.scalars().all()
    return [
        EditionResponse(
            id=e.id,
            date=e.date,
            title=e.title,
            introduction=e.introduction,
            status=e.status,
            low_signal_notice=e.low_signal_notice,
            created_at=e.created_at,
            updated_at=e.updated_at,
            published_at=e.published_at,
            story_count=len(e.stories),
        )
        for e in editions
    ]

@router.get("/stories/{edition_date}/{slug}", response_model=StoryResponse)
async def get_story_by_slug(edition_date: date, slug: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Story)
        .join(Edition, Edition.id == Story.edition_id)
        .where(Edition.date == edition_date, Story.slug == slug, Story.status == "published")
        .options(selectinload(Story.sources), selectinload(Story.categories))
    )
    res = await db.execute(stmt)
    story = res.scalar_one_or_none()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    return await build_story_response(story, db)

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Category, func.count(story_categories.c.story_id).label("count"))
        .outerjoin(story_categories, story_categories.c.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )
    res = await db.execute(stmt)
    items = []
    for cat, count in res.fetchall():
        items.append(CategoryResponse(id=cat.id, name=cat.name, slug=cat.slug, story_count=count))
    return items

@router.get("/categories/{slug}", response_model=List[StoryResponse])
async def get_stories_by_category(slug: str, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Story)
        .join(story_categories, story_categories.c.story_id == Story.id)
        .join(Category, Category.id == story_categories.c.category_id)
        .where(Category.slug == slug, Story.status == "published")
        .options(selectinload(Story.sources), selectinload(Story.categories))
        .order_by(Story.published_at.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    stories = res.scalars().all()
    return [await build_story_response(s, db) for s in stories]

@router.get("/search", response_model=List[StoryResponse])
async def search_stories(q: str = Query(..., min_length=2), limit: int = 25, db: AsyncSession = Depends(get_db)):
    # Full-text search with fallback to ILIKE
    query_str = q.strip()
    try:
        ts_stmt = (
            select(Story)
            .where(
                Story.status == "published",
                text("to_tsvector('english', stories.title || ' ' || stories.summary || ' ' || stories.why_it_matters) @@ plainto_tsquery('english', :q)"),
            )
            .params(q=query_str)
            .options(selectinload(Story.sources), selectinload(Story.categories))
            .limit(limit)
        )
        res = await db.execute(ts_stmt)
        stories = res.scalars().all()
    except Exception:
        # ILIKE fallback
        like_q = f"%{query_str}%"
        stmt = (
            select(Story)
            .where(
                Story.status == "published",
                or_(
                    Story.title.ilike(like_q),
                    Story.summary.ilike(like_q),
                    Story.why_it_matters.ilike(like_q),
                ),
            )
            .options(selectinload(Story.sources), selectinload(Story.categories))
            .limit(limit)
        )
        res = await db.execute(stmt)
        stories = res.scalars().all()

    return [await build_story_response(s, db) for s in stories]

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(data: FeedbackSubmitRequest, db: AsyncSession = Depends(get_db)):
    try:
        res = await FeedbackService.record_vote(
            session=db,
            story_id=data.story_id,
            vote=data.vote,
            session_id=data.session_id,
        )
        return FeedbackResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
