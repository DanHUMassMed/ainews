"""Research Agent for Deep Technical Extraction.

PRD 2.0 Section 21: Extracts clean markdown from candidate URLs using Firecrawl,
resolves primary sources (arXiv, GitHub, engineering blogs), and produces
factual technical dossiers.
"""

import json
from typing import List, Dict, Any, Optional
from google.adk.agents import LlmAgent
from agents.app.config import get_agent_model
from agents.app.tools.firecrawl_tool import scrape_webpage

RESEARCH_INSTRUCTION = """You are the Research Agent for AI Industry News Daily.
Your mission is to perform deep technical research on candidate story URLs.

Key Responsibilities:
1. Scrape the full primary source document or article using `scrape_webpage`.
2. Extract the core architectural details, benchmark numbers, model weights licenses, throughput improvements, or policy texts.
3. Identify the true primary source URL (e.g. arXiv paper, GitHub repository, official company announcement) rather than aggregator summaries.
4. Synthesize a structured factual dossier containing:
   - title
   - primary_source (canonical URL)
   - secondary_sources (list of related links or benchmarks)
   - technical_summary (2-3 concise paragraphs of concrete facts)
   - key_claims (bulleted claims with evidence)
   - covered_entities (companies, labs, models, hardware mentioned)

Do NOT accept vague marketing buzzwords at face value. Extract verifiable claims.
"""

def create_research_agent() -> LlmAgent:
    """Factory to instantiate the configured Research LlmAgent."""
    return LlmAgent(
        name="ResearchAgent",
        model=get_agent_model("research"),
        instruction=RESEARCH_INSTRUCTION,
        tools=[scrape_webpage],
    )
