"""Tests for Production Whitelist Service and Feed Ingestion."""

import pytest
from backend.app.services.whitelist import WhitelistService, WhitelistEntry
from backend.app.services.feed_ingestion import FeedIngestionService
from agents.app.tools.whitelist_tool import check_whitelist_status

SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Latent Space</title>
    <link>https://www.latent.space</link>
    <item>
      <title>Forward Deployed Engineers: The Secret Weapon</title>
      <link>https://www.latent.space/p/forward-deployed-engineer-best-practices</link>
      <guid>https://www.latent.space/p/forward-deployed-engineer-best-practices</guid>
      <pubDate>Fri, 11 Sep 2026 12:00:00 GMT</pubDate>
      <enclosure url="https://substackcdn.com/image/hero_img.png" type="image/png" />
      <description>Deep dive into enterprise AI deployment paradigms.</description>
      <content:encoded><![CDATA[<p>Full article markdown body discussing LLM production pipelines.</p>]]></content:encoded>
    </item>
  </channel>
</rss>
"""

SAMPLE_ATOM_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Simon Willison's Weblog</title>
  <link href="https://simonwillison.net/"/>
  <entry>
    <title>OpenAI Agents SDK Architecture</title>
    <link rel="alternate" href="https://simonwillison.net/2026/Sep/12/openai-agents-sdk/"/>
    <id>tag:simonwillison.net,2026-09-12:openai-agents-sdk</id>
    <updated>2026-09-12T14:00:00Z</updated>
    <summary>Exploring the new tool execution and memory primitives in OpenAI's agent SDK.</summary>
    <content type="html"><![CDATA[<p>Here is an architectural breakdown with <img src="https://simonwillison.net/static/diag.png" /> diagram.</p>]]></content>
  </entry>
</feed>
"""

def test_whitelist_service_loads_production_data():
    """Verify WhitelistService loads entries from backend/app/data/whitelist.csv."""
    sources = WhitelistService.get_all_sources()
    assert len(sources) >= 35, f"Expected at least 35 verified sources, got {len(sources)}"
    
    # Check key primary labs exist
    domains = [s.domain for s in sources]
    assert "openai.com" in domains
    assert "anthropic.com" in domains
    assert "deepmind.google" in domains
    assert "qwenlm.github.io" in domains
    assert "semianalysis.com" in domains

def test_whitelist_domain_matching():
    """Verify domain extraction and tier classification."""
    assert WhitelistService.is_whitelisted_domain("https://openai.com/news/some-post") is True
    assert WhitelistService.is_whitelisted_domain("https://blogs.nvidia.com/blog/2026/09/nemotron/") is True
    assert WhitelistService.is_whitelisted_domain("https://unverified-random-spam-blog.xyz") is False

    entry = WhitelistService.get_source_for_url("https://semianalysis.com/p/gpu-economics")
    assert entry is not None
    assert entry.tier == "Tier 2"
    assert entry.ingestion_strategy == "rss_feed"

def test_whitelist_tool_check_status():
    """Verify ADK whitelist verification tool."""
    res = check_whitelist_status("https://latent.space/p/mcp-guide")
    assert res["is_whitelisted"] is True
    assert res["tier"] == "Tier 3"
    assert res["ingestion_strategy"] == "rss_feed"

    unknown = check_whitelist_status("https://unknown-domain.com")
    assert unknown["is_whitelisted"] is False
    assert unknown["tier"] == "Unlisted"

def test_feed_ingestion_rss_parsing():
    """Verify FeedIngestionService parses RSS 2.0 with canonical link and enclosure."""
    entry = WhitelistEntry(
        url_path="latent.space",
        tier="Tier 3",
        category="AI Engineering",
        ingestion_strategy="rss_feed",
    )
    items = FeedIngestionService.parse_rss_or_atom(SAMPLE_RSS_XML, entry)
    assert len(items) == 1
    item = items[0]

    # Verify canonical link is the public web page (NOT the .xml feed)
    assert item["raw_url"] == "https://www.latent.space/p/forward-deployed-engineer-best-practices"
    assert item["url"] == "https://latent.space/p/forward-deployed-engineer-best-practices"
    assert item["title"] == "Forward Deployed Engineers: The Secret Weapon"
    assert item["image_url"] == "https://substackcdn.com/image/hero_img.png"
    assert "Full article markdown body" in item["content"]
    assert item["tier"] == "Tier 3"

def test_feed_ingestion_atom_parsing():
    """Verify FeedIngestionService parses Atom feeds with alternate link and inline images."""
    entry = WhitelistEntry(
        url_path="simonwillison.net",
        tier="Tier 3",
        category="AI Engineering",
        ingestion_strategy="rss_feed",
    )
    items = FeedIngestionService.parse_rss_or_atom(SAMPLE_ATOM_XML, entry)
    assert len(items) == 1
    item = items[0]

    # Verify canonical link is the blog post permalink
    assert item["raw_url"] == "https://simonwillison.net/2026/Sep/12/openai-agents-sdk/"
    assert item["url"] == "https://simonwillison.net/2026/Sep/12/openai-agents-sdk"
    assert item["title"] == "OpenAI Agents SDK Architecture"
    assert item["image_url"] == "https://simonwillison.net/static/diag.png"
    assert "architectural breakdown" in item["content"]

def test_secondary_discovery_classification():
    """Verify paywalled outlets are marked for secondary discovery only."""
    sec_sources = WhitelistService.get_secondary_discovery_sources()
    sec_domains = [s.domain for s in sec_sources]
    
    assert "bloomberg.com" in sec_domains
    assert "theinformation.com" in sec_domains
    assert "wsj.com" in sec_domains
    assert "ft.com" in sec_domains
