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
