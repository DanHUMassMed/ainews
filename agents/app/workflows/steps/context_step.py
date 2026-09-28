"""Context initialization step for editorial workflow."""

from typing import Dict, Any
from agents.app.tools.editorial_mcp_tool import get_editorial_context


class ContextStep:
    """Initializes editorial context, historical memory, and feedback analytics."""

    async def execute(self, lookback_days: int = 28) -> Dict[str, Any]:
        """Fetch editorial context, scoring weights, guidelines, and feedback analytics."""
        try:
            return await get_editorial_context(lookback_days=lookback_days)
        except Exception:
            return {"scoring_weights": {}, "repetition_avoid_topics": [], "feedback_analytics": {}}
