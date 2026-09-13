"""Discovery Agent for AI News Ecosystem.

PRD 2.0 Section 20: Searches whitelisted feeds, metasearch engines across AI focus areas,
deduplicates URLs, and identifies potential candidate news items.
"""

import json
from typing import List, Dict, Any, Optional
from google.adk.agents import LlmAgent
from agents.app.config import get_agent_model
from agents.app.tools.searxng_tool import search_web, run_discovery_matrix
from agents.app.tools.feed_tool import ingest_whitelisted_feeds, ingest_arxiv_preprints, ingest_community_pulse
from agents.app.tools.whitelist_tool import check_whitelist_status
from agents.app.tools.editorial_mcp_tool import fetch_editorial_memory

DISCOVERY_INSTRUCTION = """You are the Discovery Agent for AI Industry News Daily.
Your goal is to uncover high-signal, consequential AI engineering, research, and infrastructure announcements.

Key Responsibilities:
1. Ingest clean, verified announcements directly from whitelisted primary lab feeds, Substack newsletters, and engineering blogs.
2. Query key focus areas (frontier LLMs, open-weights models, AI chip hardware, distributed inference/training frameworks, autonomous robotics, AI governance) via SearXNG.
3. Validate candidate URLs against the publication whitelist to prioritize authoritative Tier 1-3 sources.
4. Filter out consumer PR fluff, clickbait listicles, speculation, and low-substance rumors.
5. Extract candidate leads with title, canonical URL, snippet, and discovered topic.
6. Check editorial memory to avoid topics or entities recently oversaturated.

When invoked, gather recent breakthroughs (past 24-48 hours) and return a structured JSON list of candidate leads.
"""

def create_discovery_agent() -> LlmAgent:
    """Factory to instantiate the configured Discovery LlmAgent."""
    return LlmAgent(
        name="DiscoveryAgent",
        model=get_agent_model("discovery"),
        instruction=DISCOVERY_INSTRUCTION,
        tools=[
            ingest_whitelisted_feeds,
            ingest_arxiv_preprints,
            ingest_community_pulse,
            search_web,
            run_discovery_matrix,
            check_whitelist_status,
            fetch_editorial_memory,
        ],
    )
