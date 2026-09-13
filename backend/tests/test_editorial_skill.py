import pytest
from datetime import date, timedelta
from backend.app.core.config import settings

@pytest.mark.asyncio
async def test_editorial_auth_failure(async_client):
    # No auth header -> 401
    resp = await async_client.post("/api/editorial/context", json={})
    assert resp.status_code == 401

    # Invalid token -> 403
    resp_bad = await async_client.post(
        "/api/editorial/context",
        json={},
        headers={"Authorization": "Bearer bad_invalid_token"}
    )
    assert resp_bad.status_code == 403

@pytest.mark.asyncio
async def test_get_editorial_context_success(async_client):
    resp = await async_client.post(
        "/api/editorial/context",
        json={"days_lookback": 28},
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "publication_date" in data
    assert "scoring_weights" in data
    assert "portfolio_targets" in data

@pytest.mark.asyncio
async def test_stage_draft_and_status(async_client):
    import uuid
    test_suffix = uuid.uuid4().hex[:6]
    import random
    today = (date.today() + timedelta(days=random.randint(50001, 90000))).isoformat()
    draft_payload = {
        "date": today,
        "title": "Today in AI: Autonomous Breakthroughs",
        "introduction": "Key technical shifts across open weights and inference architecture.",
        "stories": [
            {
                "title": "DeepSeek Unveils Open Mixture-of-Experts Architecture with Near-Zero Overhead",
                "slug": f"deepseek-open-moe-architecture-{test_suffix}",
                "summary": "DeepSeek has released an open architecture that significantly reduces MoE routing communication overhead across distributed compute clusters.",
                "why_it_matters": "Lowers multi-node training and inference barriers for open weights, challenging proprietary frontier systems.",
                "body": "Detailed technical analysis of the sparse kernel dispatch...",
                "is_lead": True,
                "position": 0,
                "category_slugs": ["ai-models", "open-ai"],
                "sources": [
                    {
                        "url": "https://arxiv.org/abs/2026.12345",
                        "title": "DeepSeek MoE Technical Paper",
                        "publisher": "arXiv"
                    }
                ]
            },
            {
                "title": "TSMC Begins High-Volume Production of 2nm AI Accelerator Wafers",
                "slug": f"tsmc-2nm-accelerator-production-{test_suffix}",
                "summary": "TSMC has confirmed volume packaging for next-generation custom accelerators with substantial thermal efficiency gains.",
                "why_it_matters": "Directly impacts 2027 datacenter power budgets and hardware availability for hyperscale inference.",
                "body": "The 2nm process node introduces backside power delivery...",
                "is_lead": False,
                "position": 1,
                "category_slugs": ["hardware", "infrastructure"],
                "sources": [
                    {
                        "url": "https://hardwarenews.com/tsmc-2nm",
                        "title": "TSMC 2nm Press Release",
                        "publisher": "Tech Wire"
                    }
                ]
            }
        ]
    }

    # Stage draft
    stage_resp = await async_client.post(
        "/api/editorial/draft",
        json=draft_payload,
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert stage_resp.status_code == 200
    edition = stage_resp.json()
    edition_id = edition["id"]

    # Check status (should fail validation because fewer than 5 stories and not marked low-signal)
    status_resp = await async_client.get(
        f"/api/editorial/edition/{edition_id}/status",
        headers={"Authorization": f"Bearer {settings.EDITORIAL_SECRET_KEY}"}
    )
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["is_valid"] is False
    assert any("at least 5 stories" in err for err in status_data["validation_errors"])
