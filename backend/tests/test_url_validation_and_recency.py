import pytest
from datetime import datetime, timezone, timedelta, date
from backend.app.services.url_validator import URLValidatorService
from backend.app.services.publisher import PublicationGateService
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.models.source import Source

@pytest.mark.asyncio
async def test_url_validator_service_real_and_broken():
    # Valid URL should pass
    is_valid, code, final_url, err = await URLValidatorService.validate_url("https://github.com/vllm-project/vllm")
    assert is_valid is True
    assert 200 <= code < 300
    assert err is None

    # Broken 404 URL should fail
    is_valid_404, code_404, _, err_404 = await URLValidatorService.validate_url("https://github.com/nonexistent-org-404-broken-ainews-link")
    assert is_valid_404 is False
    assert code_404 == 404 or "404" in (err_404 or "")

    # Invalid scheme should fail immediately
    is_valid_bad, _, _, err_bad = await URLValidatorService.validate_url("ftp://invalid-scheme.com")
    assert is_valid_bad is False
    assert "Invalid URL scheme" in err_bad

def test_publication_gate_rejects_stale_story():
    now = datetime.now(timezone.utc)
    target_date = date(2026, 9, 9)
    # Story published 2 years ago (stale)
    stale_date = datetime(2024, 9, 9, tzinfo=timezone.utc)

    edition = Edition(
        date=target_date,
        title="AI Industry Briefing Test",
        low_signal_notice="Low signal testing",
        stories=[
            Story(
                title="Stale Historical Story",
                slug="stale-historical-story",
                summary="This is an extensive summary of an old development from two years ago.",
                why_it_matters="Critical implications that occurred years ago in past cycles.",
                is_lead=True,
                published_at=stale_date,
                sources=[Source(url="https://github.com/vllm-project/vllm", title="vLLM")]
            )
        ]
    )

    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is False
    assert any("story is stale" in err for err in errors)

def test_publication_gate_approves_fresh_story():
    target_date = date(2026, 9, 9)
    # Story published today or yesterday
    fresh_date = datetime(2026, 9, 9, 8, 30, tzinfo=timezone.utc)

    edition = Edition(
        date=target_date,
        title="AI Industry Briefing Test",
        low_signal_notice="Low signal testing",
        stories=[
            Story(
                title="Fresh Breakthrough Architecture",
                slug="fresh-breakthrough-architecture",
                summary="This is an extensive summary of a brand new development from today.",
                why_it_matters="Critical implications for engineering teams deploying models today.",
                is_lead=True,
                published_at=fresh_date,
                sources=[Source(url="https://github.com/vllm-project/vllm", title="vLLM")]
            )
        ]
    )

    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is True
    assert len(errors) == 0
