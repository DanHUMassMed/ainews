"""Specialized Editorial Agents for AI Industry News Daily.

PRD 2.0 Section 19: Six specialized agents operating over Google ADK 2.x and LiteLLM:
1. DiscoveryAgent: Metasearch ecosystem discovery and lead gathering.
2. ResearchAgent: Deep markdown scraping, primary source resolution, and dossier synthesis.
3. EvaluationAgent: Multi-factor dimensional scoring and portfolio tiering.
4. SelectionAgent: Lineup assembly, lead selection, diversity enforcement, and low-signal handling.
5. WritingAgent: Authoring technical briefings and "Why It Matters" synthesis.
6. CriticAgent: Adversarial verification, hype elimination, and publication gate checks.
"""

from agents.app.agents.discovery import create_discovery_agent, DISCOVERY_INSTRUCTION
from agents.app.agents.research import create_research_agent, RESEARCH_INSTRUCTION
from agents.app.agents.evaluation import create_evaluation_agent, EVALUATION_INSTRUCTION
from agents.app.agents.selection import (
    create_selection_agent,
    SELECTION_INSTRUCTION,
    select_edition_lineup,
    select_edition_lineup_algorithmic,
    extract_source_entity,
)
from agents.app.agents.writing import (
    create_writing_agent,
    WRITING_INSTRUCTION,
    synthesize_story,
    review_and_refine_story,
    synthesize_newspaper_article_algorithmic,
    sanitize_story_completeness,
    audit_story_draft,
    clean_source_text,
    clean_sentence_closure,
    format_newspaper_headline,
    clean_markdown_headings_from_prose,
    format_body_markdown,
)
from agents.app.agents.critic import create_critic_agent, CRITIC_INSTRUCTION

__all__ = [
    "create_discovery_agent",
    "create_research_agent",
    "create_evaluation_agent",
    "create_selection_agent",
    "create_writing_agent",
    "create_critic_agent",
    "select_edition_lineup",
    "select_edition_lineup_algorithmic",
    "extract_source_entity",
    "synthesize_story",
    "review_and_refine_story",
    "synthesize_newspaper_article_algorithmic",
    "sanitize_story_completeness",
    "audit_story_draft",
    "clean_source_text",
    "clean_sentence_closure",
    "format_newspaper_headline",
    "DISCOVERY_INSTRUCTION",
    "RESEARCH_INSTRUCTION",
    "EVALUATION_INSTRUCTION",
    "SELECTION_INSTRUCTION",
    "WRITING_INSTRUCTION",
    "CRITIC_INSTRUCTION",
]
