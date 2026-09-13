"""Selection Agent for Portfolio Allocation and Edition Assembly.

PRD 2.0 Section 23: Enforces portfolio allocation (70% Core, 20% Exploratory, 10% Contrarian),
selects exactly 1 lead story and 2-6 secondary stories, ensures category diversity,
and handles low-signal day constraints.
"""

import json
from typing import List, Dict, Any, Optional
from google.adk.agents import LlmAgent
from agents.app.config import get_agent_model
from agents.app.tools.editorial_mcp_tool import fetch_editorial_memory, submit_candidate_stories

SELECTION_INSTRUCTION = """You are the Selection Agent for AI Industry News Daily.
You assemble the daily edition lineup from evaluated candidate stories.

Lineup Rules:
1. Story Count:
   - Exactly 3 to 7 stories total (target 5).
   - Exactly 1 Lead Story.
   - 2 to 6 Secondary Stories.
2. Portfolio Allocation:
   - ~70% Core stories (foundational architecture releases, verifiable breakthroughs).
   - ~20% Exploratory stories (novel research, speculative hardware, early prototypes).
   - ~10% Contrarian stories (rigorous critique, benchmark failures, counter-narratives).
3. Lead Story Criteria:
   - Highest composite score combined with highest novelty and evidence.
   - Sets the tone for the edition: must be an undeniable event of industry-wide importance.
4. Diversity Constraints:
   - Maximum 2 stories in the same primary category.
   - Do NOT select multiple stories covering the exact same corporate entity unless addressing distinct breakthroughs.
5. Low-Signal Day Rule (PRD Section 35):
   - If fewer than 3 stories meet the minimum quality threshold (composite score >= 6.0, evidence >= 5.0), do NOT pad the edition with filler.
   - Instead, stage an abbreviated edition with an explicit `low_signal_notice` explaining to readers that today was a quiet news cycle and quality standards were maintained.
6. Record Audit Trail:
   - Submit all candidates (both selected and rejected with rejection reason) to `submit_candidate_stories`.
"""

def create_selection_agent() -> LlmAgent:
    """Factory to instantiate the configured Selection LlmAgent."""
    return LlmAgent(
        name="SelectionAgent",
        model=get_agent_model("selection"),
        instruction=SELECTION_INSTRUCTION,
        tools=[fetch_editorial_memory, submit_candidate_stories],
    )
