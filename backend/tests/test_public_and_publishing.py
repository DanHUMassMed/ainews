import pytest
import uuid
from datetime import date, timedelta
from backend.app.core.config import settings

@pytest.mark.asyncio
async def test_health_check(async_client):
    resp = await async_client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_public_categories_list(async_client):
    resp = await async_client.get("/api/public/categories")
    assert resp.status_code == 200
    categories = resp.json()
    assert len(categories) >= 12
    slugs = [c["slug"] for c in categories]
    assert "ai-models" in slugs
    assert "open-ai" in slugs
    assert "infrastructure" in slugs

@pytest.mark.asyncio
async def test_candidate_batch_submit_and_query(async_client):
    candidates_payload = {
        "run_id": "test_run_001",
        "candidates": [
            {
                "url": "https://example.com/research-paper-1",
                "title": "Novel Sparse Attention Mechanism for Long-Context LLMs",
                "raw_text": "Extracted text content...",
                "scores": {
                    "significance": 8.5,
                    "novelty": 8.0,
                    "evidence": 9.0,
                    "saturation": 2.0,
                    "feedback_bias": 0.0
                },
                "selected": True,
                "rejected_reason": None
            },
            {
                "url": "https://example.com/minor-update",
                "title": "Startup X Releases Minor UI Update for Chat App",
                "scores": {
                    "significance": 2.0,
                    "novelty": 2.0,
                    "evidence": 4.0,
                    "saturation": 7.0,
                    "feedback_bias": -1.0
                },
                "selected": False,
                "rejected_reason": "Low significance and high mainstream marketing saturation"
            }
        ]
    }

    # Submit candidates
    submit_resp = await async_client.post(
        "/api/editorial/candidates",
        json=candidates_payload,
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert submit_resp.status_code == 200
    assert submit_resp.json()["candidates_saved"] == 2

    # Query candidate audit list
    list_resp = await async_client.get(
        "/api/editorial/candidates",
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert list_resp.status_code == 200
    candidates = list_resp.json()
    assert len(candidates) >= 2
    titles = [c["title"] for c in candidates]
    assert "Novel Sparse Attention Mechanism for Long-Context LLMs" in titles

@pytest.mark.asyncio
async def test_full_draft_staging_and_publishing_flow(async_client):
    test_suffix = uuid.uuid4().hex[:6]
    import random
    today = (date.today() + timedelta(days=random.randint(500, 50000))).isoformat()
    # 5 full stories meeting publication gate rules
    stories = []
    for i in range(5):
        stories.append({
            "title": f"Significant AI Technical Advance Number {i+1} in Infrastructure",
            "slug": f"advance-{i+1}-infrastructure-{test_suffix}",
            "summary": f"This is an in-depth summary of breakthrough development number {i+1} detailing concrete architectural consequences for latency budgets, high-throughput batching, and energy efficiency across distributed GPU compute clusters.",
            "why_it_matters": f"Practical deployment implications for engineers running large-scale distributed inference systems {i+1}.",
            "body": f"### Architectural Analysis\n\nStory {i+1} provides complete technical details, memory hierarchy optimizations, and multi-node execution profiles across diverse distributed compute clusters.\n\n### Scaling & Deployment\n\nComprehensive evaluation of production latency bounds, token economics, and error recovery dynamics for enterprise deployments.\n\n### Operational Takeaways\n\nInfrastructure engineering teams should benchmark throughput against peak SRAM bandwidth allocations before committing to full cluster migration.",
            "is_lead": (i == 0),
            "position": i,
            "category_slugs": ["infrastructure"],
            "sources": [
                {
                    "url": f"https://example.com/source-{i+1}",
                    "title": f"Primary Source {i+1}",
                    "publisher": "Tech Journal"
                }
            ]
        })

    stage_resp = await async_client.post(
        "/api/editorial/draft",
        json={
            "date": today,
            "title": "Daily Briefing: Major AI Advancements",
            "introduction": "Today's briefing highlighting critical shifts in AI infrastructure.",
            "stories": stories
        },
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert stage_resp.status_code == 200
    edition = stage_resp.json()
    edition_id = edition["id"]

    # Validate status (should now be valid since 5 stories, 1 lead, valid sources & why_it_matters)
    status_resp = await async_client.get(
        f"/api/editorial/edition/{edition_id}/status",
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["is_valid"] is True
    assert len(status_data["validation_errors"]) == 0

    # Publish edition
    pub_resp = await async_client.post(
        f"/api/editorial/edition/{edition_id}/publish",
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert pub_resp.status_code == 200
    assert pub_resp.json()["status"] == "published"

    # Verify today's edition is publicly visible
    today_pub_resp = await async_client.get(f"/api/public/editions/{today}")
    assert today_pub_resp.status_code == 200
    today_data = today_pub_resp.json()
    assert today_data["id"] == edition_id
    assert today_data["lead_story"] is not None
    assert len(today_data["stories"]) == 5

    # Test voting on lead story
    lead_story_id = today_data["lead_story"]["id"]
    vote_resp = await async_client.post(
        "/api/public/feedback",
        json={
            "story_id": lead_story_id,
            "vote": 1,
            "session_id": "test_reader_session_abc"
        }
    )
    assert vote_resp.status_code == 200
    assert vote_resp.json()["upvotes"] >= 1

    # Test vote idempotency with same session (change vote to -1)
    revote_resp = await async_client.post(
        "/api/public/feedback",
        json={
            "story_id": lead_story_id,
            "vote": -1,
            "session_id": "test_reader_session_abc"
        }
    )
    assert revote_resp.status_code == 200
    assert revote_resp.json()["downvotes"] >= 1

    # Verify permanent story URL
    lead_slug = today_data["lead_story"]["slug"]
    story_url_resp = await async_client.get(f"/api/public/stories/{today}/{lead_slug}")
    assert story_url_resp.status_code == 200
    assert story_url_resp.json()["id"] == lead_story_id

    # Verify search
    search_resp = await async_client.get("/api/public/search?q=Infrastructure")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1
