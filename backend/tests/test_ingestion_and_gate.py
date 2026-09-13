import pytest
from datetime import date
from backend.app.services.searxng import SearXNGClient
from backend.app.services.firecrawl import FirecrawlClient
from backend.app.services.publisher import PublicationGateService
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.models.source import Source

@pytest.mark.asyncio
async def test_searxng_live_search():
    client = SearXNGClient()
    results = await client.search("NVIDIA Blackwell GPU cluster infrastructure", max_results=5)
    assert isinstance(results, list)
    if results:
        first = results[0]
        assert "url" in first
        assert "title" in first
        assert not first["url"].startswith("http://localhost")

@pytest.mark.asyncio
async def test_firecrawl_live_scrape():
    client = FirecrawlClient()
    res = await client.scrape_url("https://example.com")
    assert res["success"] is True
    assert "Example Domain" in res["markdown"]

def test_publication_gate_rejects_empty():
    edition = Edition(date=date.today(), title="Empty Draft", status="draft")
    edition.stories = []
    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is False
    assert any("zero stories" in err for err in errors)

def test_publication_gate_rejects_missing_why_it_matters():
    edition = Edition(date=date.today(), title="Test Edition", status="draft", low_signal_notice="Low-signal notice")
    story = Story(
        slug="story-1",
        title="Valid Headline That Is Long Enough",
        summary="This is an adequate length summary of the technical event.",
        why_it_matters="", # Missing!
        body="Body content here...",
        is_lead=True,
    )
    story.sources = [Source(url="https://example.com/source1")]
    edition.stories = [story]

    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is False
    assert any("Why It Matters" in err for err in errors)

def test_publication_gate_rejects_missing_sources():
    edition = Edition(date=date.today(), title="Test Edition", status="draft", low_signal_notice="Low-signal notice")
    story = Story(
        slug="story-1",
        title="Valid Headline That Is Long Enough",
        summary="This is an adequate length summary of the technical event.",
        why_it_matters="Adequate explanation of the practical consequences and implications.",
        body="Body content here...",
        is_lead=True,
    )
    story.sources = [] # Missing!
    edition.stories = [story]

    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is False
    assert any("missing required primary source" in err for err in errors)

def test_publication_gate_rejects_duplicate_slugs():
    edition = Edition(date=date.today(), title="Test Edition", status="draft", low_signal_notice="Low-signal notice")
    s1 = Story(
        slug="same-slug",
        title="First Story Headline That Is Long Enough",
        summary="This is an adequate length summary of the technical event.",
        why_it_matters="Adequate explanation of the practical consequences and implications.",
        body="Body content here...",
        is_lead=True,
    )
    s1.sources = [Source(url="https://example.com/1")]

    s2 = Story(
        slug="same-slug", # Duplicate!
        title="Second Story Headline That Is Long Enough",
        summary="This is an adequate length summary of the technical event.",
        why_it_matters="Adequate explanation of the practical consequences and implications.",
        body="Body content here...",
        is_lead=False,
    )
    s2.sources = [Source(url="https://example.com/2")]
    edition.stories = [s1, s2]

    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is False
    assert any("duplicate slug" in err for err in errors)

def test_publication_gate_approves_low_signal_compliant():
    edition = Edition(date=date.today(), title="Low Signal Edition", status="draft", low_signal_notice="Official low signal notice")
    story = Story(
        slug="clean-story-1",
        title="High Impact Development in Local AI Inference",
        summary="This is an in-depth summary of breakthrough development detailing consequences for latency.",
        why_it_matters="Practical deployment implications for engineers running large-scale distributed inference systems.",
        body="Full body analysis...",
        is_lead=True,
    )
    story.sources = [Source(url="https://example.com/clean-source")]
    edition.stories = [story]

    is_valid, errors = PublicationGateService.validate_edition_structure(edition)
    assert is_valid is True
    assert len(errors) == 0
