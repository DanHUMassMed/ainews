"""Selection step delegating to the Selection Agent for portfolio balance and diversity."""

from typing import List, Dict, Any, Optional, Tuple


class SelectionStep:
    """Reviews entire newsletter layout, enforces portfolio balance, and handles low-signal day constraints."""

    def __init__(self, live: bool = False):
        self.live = live

    async def execute(
        self,
        evaluated_candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        from agents.app.agents.selection import select_edition_lineup

        return await select_edition_lineup(
            evaluated_candidates,
            context=context,
            live=self.live,
            min_stories=5,
            max_stories=7,
        )
