import uuid
import random
from datetime import timedelta
from datetime import date
import pytest
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.models.feedback import Feedback
from backend.app.services.feedback import FeedbackService

@pytest.mark.asyncio
async def test_feedback_service_batch_votes_empty(db_session):
    """Verify batch vote query handles empty story list without error."""
    res = await FeedbackService.get_stories_votes_batch(db_session, [])
    assert res == {}

@pytest.mark.asyncio
async def test_feedback_service_batch_votes_calculation(db_session):
    """Verify single-query batch vote aggregation aggregates upvotes and downvotes accurately."""
    test_edition = Edition(
        id=uuid.uuid4(),
        date=date.today() + timedelta(days=random.randint(10000, 500000)),
        title="Test Batch Edition",
        status="published"
    )
    db_session.add(test_edition)

    story_1 = Story(
        id=uuid.uuid4(),
        edition_id=test_edition.id,
        slug=f"story-1-{uuid.uuid4().hex[:6]}",
        title="Batch Test Story 1",
        summary="Summary 1",
        body="Body 1", why_it_matters="Why 1" 
    )
    story_2 = Story(
        id=uuid.uuid4(),
        edition_id=test_edition.id,
        slug=f"story-2-{uuid.uuid4().hex[:6]}",
        title="Batch Test Story 2",
        summary="Summary 2",
        body="Body 2", why_it_matters="Why 2" 
    )
    story_3 = Story(
        id=uuid.uuid4(),
        edition_id=test_edition.id,
        slug=f"story-3-{uuid.uuid4().hex[:6]}",
        title="Batch Test Story 3",
        summary="Summary 3",
        body="Body 3", why_it_matters="Why 3" 
    )
    db_session.add_all([story_1, story_2, story_3])
    await db_session.flush()

    # Add feedback records:
    # story 1: 3 up (+1), 1 down (-1)
    # story 2: 0 up, 2 down (-1)
    # story 3: 0 up, 0 down
    feedbacks = [
        Feedback(story_id=story_1.id, vote=1, session_id="s1"),
        Feedback(story_id=story_1.id, vote=1, session_id="s2"),
        Feedback(story_id=story_1.id, vote=1, session_id="s3"),
        Feedback(story_id=story_1.id, vote=-1, session_id="s4"),
        Feedback(story_id=story_2.id, vote=-1, session_id="s5"),
        Feedback(story_id=story_2.id, vote=-1, session_id="s6"),
    ]
    db_session.add_all(feedbacks)
    await db_session.commit()

    # Test batch aggregation
    batch_counts = await FeedbackService.get_stories_votes_batch(
        db_session, [story_1.id, story_2.id, story_3.id]
    )

    assert batch_counts[story_1.id] == (3, 1)
    assert batch_counts[story_2.id] == (0, 2)
    assert batch_counts[story_3.id] == (0, 0)

    # Test single-story helper
    single_1 = await FeedbackService.get_story_votes(db_session, story_1.id)
    single_2 = await FeedbackService.get_story_votes(db_session, story_2.id)
    single_3 = await FeedbackService.get_story_votes(db_session, story_3.id)

    assert single_1 == (3, 1)
    assert single_2 == (0, 2)
    assert single_3 == (0, 0)

@pytest.mark.asyncio
async def test_feedback_service_get_analytics_all_categories(db_session):
    """Verify get_analytics returns all domain categories even if they have 0 votes."""
    analytics = await FeedbackService.get_analytics(db_session, window_days=30)
    assert analytics.categories is not None
    assert len(analytics.categories) >= 12
    slugs = [c.slug for c in analytics.categories]
    assert "hardware" in slugs
    assert "ai-models" in slugs
    assert "open-source" in slugs
    assert "research" in slugs

    # Each category should have total_votes, raw_bias, and effective_bias
    for c in analytics.categories:
        assert c.total_votes == c.upvotes + c.downvotes
        assert -3.0 <= c.raw_bias <= 3.0
        assert -3.0 <= c.effective_bias <= 3.0

@pytest.mark.asyncio
async def test_feedback_service_vote_crud_and_overrides(db_session):
    """Verify vote update, deletion, and category editorial overrides."""
    # 1. Create a story to vote on
    test_edition = Edition(
        id=uuid.uuid4(),
        date=date.today() + timedelta(days=random.randint(500001, 999999)),
        title="Test CRUD Edition",
        status="published"
    )
    db_session.add(test_edition)
    story = Story(
        id=uuid.uuid4(),
        edition_id=test_edition.id,
        slug=f"crud-story-{uuid.uuid4().hex[:6]}",
        title="CRUD Test Story",
        summary="Summary",
        body="Body",
        why_it_matters="Why"
    )
    db_session.add(story)
    await db_session.flush()

    # Record vote
    rec = await FeedbackService.record_vote(db_session, story.id, 1, "test_crud_sess")
    assert rec["status"] == "recorded"
    assert rec["upvotes"] == 1

    # Fetch history
    history = await FeedbackService.get_history(db_session, limit=10, days=30)
    matching = [h for h in history if h["story_id"] == str(story.id)]
    assert len(matching) >= 1
    feedback_id = uuid.UUID(matching[0]["id"])

    # Update vote to -1
    upd = await FeedbackService.update_vote(db_session, feedback_id, -1)
    assert upd["status"] == "updated"
    assert upd["vote"] == -1

    # Set Category Override
    ovr = await FeedbackService.set_category_override(
        db_session,
        slug="hardware",
        manual_bias=1.75,
        active=True,
        reason="Prioritize next-gen hardware architectures"
    )
    assert "hardware" in ovr
    assert ovr["hardware"]["manual_bias"] == 1.75
    assert ovr["hardware"]["active"] is True

    # Check analytics reflects override
    analytics = await FeedbackService.get_analytics(db_session, window_days=30)
    hw_cat = next((c for c in analytics.categories if c.slug == "hardware"), None)
    assert hw_cat is not None
    assert hw_cat.override_active is True
    assert hw_cat.override_bias == 1.75
    assert hw_cat.effective_bias == 1.75
    assert hw_cat.override_reason == "Prioritize next-gen hardware architectures"

    # Reset Category Override
    cleared = await FeedbackService.delete_category_override(db_session, slug="hardware")
    assert "hardware" not in cleared
    analytics_after = await FeedbackService.get_analytics(db_session, window_days=30)
    hw_after = next((c for c in analytics_after.categories if c.slug == "hardware"), None)
    assert hw_after is not None
    assert hw_after.override_active is False

    # Delete vote
    del_res = await FeedbackService.delete_vote(db_session, feedback_id)
    assert del_res["status"] == "deleted"
