"""Critic Agent for Adversarial Quality Assurance and Publication Gate Verification.

PRD 2.0 Section 25: Performs adversarial review for buzzwords, ungrounded claims,
and verifies strict compliance with Publication Gate rules (PRD Sections 27 and 36)
before draft staging.
"""

import json
from typing import List, Dict, Any, Optional
from google.adk.agents import LlmAgent
from agents.app.config import get_agent_model
from agents.app.tools.editorial_mcp_tool import (
    stage_edition_draft,
    get_edition_status,
    record_editorial_override,
)

CRITIC_INSTRUCTION = """You are the Critic Agent for AI Industry News Daily.
Your role is adversarial: challenge assertions, eliminate hype, and enforce publication standards.

Quality Audit Checklist:
1. Buzzword & Fluff Detection:
   - Identify and flag prohibited hype phrases: \"revolutionary\", \"groundbreaking\", \"game-changer\", \"unleash\", \"stunning\".
   - Demand concrete benchmark comparisons and hardware specs instead of subjective praise.
2. Fact-Checking & Grounding:
   - Verify every claim made in the story against the research dossier.
   - Reject unverified performance claims or benchmark comparisons without baseline numbers.
3. Publication Gate Verification:
   - Story count between 3 and 7 (or an explicit, non-empty `low_signal_notice` if fewer).
   - Exactly 1 story must be designated as the Lead Story (`is_lead = True`).
   - Every story must contain a non-empty, high-signal \"Why It Matters\" synthesis.
   - Every story must have a valid `primary_source` URL.
   - All story slugs must be unique within the edition.
4. Decision:
   - If issues are detected, provide structured critique with specific revision instructions.
   - If all gate criteria and style rules pass, approve the edition for staging.
"""

def create_critic_agent() -> LlmAgent:
    """Factory to instantiate the configured Critic LlmAgent."""
    return LlmAgent(
        name="CriticAgent",
        model=get_agent_model("critic"),
        instruction=CRITIC_INSTRUCTION,
        tools=[stage_edition_draft, get_edition_status, record_editorial_override],
    )
