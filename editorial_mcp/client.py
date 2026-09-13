"""
AI Industry News Daily - Editorial MCP Client
Provides programmatic typed access to the Editorial MCP Server tools.
"""

import asyncio
from typing import Dict, Any, List, Optional
from editorial_mcp.server import mcp_server

class EditorialMCPClient:
    """In-process and stdio-capable client for the Editorial MCP Server."""

    def __init__(self, server=mcp_server):
        self.server = server

    async def _call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        res = await self.server.call_tool(tool_name, arguments)
        if hasattr(res, "is_error") and res.is_error:
            raise RuntimeError(f"MCP Tool '{tool_name}' failed: {res}")
        if hasattr(res, "structured_content") and res.structured_content:
            return res.structured_content.get("result", res.structured_content)
        if hasattr(res, "content") and res.content:
            first = res.content[0]
            if hasattr(first, "text"):
                import json
                try:
                    return json.loads(first.text)
                except Exception:
                    return first.text
        return res

    async def get_editorial_context(self, lookback_days: int = 28, days_lookback: Optional[int] = None) -> Dict[str, Any]:
        eff_days = days_lookback if days_lookback is not None else lookback_days
        return await self._call("get_editorial_context", {"lookback_days": eff_days})

    async def get_feedback_analytics(self, window_days: int = 30) -> Dict[str, Any]:
        return await self._call("get_feedback_analytics", {"window_days": window_days})

    async def get_historical_feedback(self, limit: int = 50, days: int = 30) -> List[Dict[str, Any]]:
        return await self._call("get_historical_feedback", {"limit": limit, "days": days})

    async def fetch_editorial_memory(self, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self._call("fetch_editorial_memory", {"memory_type": memory_type})

    async def submit_candidate_stories(self, candidates: List[Dict[str, Any]], run_id: Optional[str] = None) -> Dict[str, Any]:
        return await self._call("submit_candidate_stories", {"candidates": candidates, "run_id": run_id})

    async def get_candidate_details(self, candidate_id: str) -> Dict[str, Any]:
        return await self._call("get_candidate_details", {"candidate_id": candidate_id})

    async def stage_edition_draft(
        self,
        date: Any = None,
        title: Optional[str] = None,
        introduction: Optional[str] = None,
        low_signal_notice: Optional[str] = None,
        stories: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if isinstance(date, dict) and not title:
            d = date
            return await self._call("stage_edition_draft", {
                "date": str(d.get("date")),
                "title": d.get("title", ""),
                "introduction": d.get("introduction", ""),
                "low_signal_notice": d.get("low_signal_notice"),
                "stories": d.get("stories") or [],
            })
        return await self._call("stage_edition_draft", {
            "date": str(date),
            "title": title or "",
            "introduction": introduction or "",
            "low_signal_notice": low_signal_notice,
            "stories": stories or [],
        })

    async def get_edition_status(self, edition_id: str) -> Dict[str, Any]:
        return await self._call("get_edition_status", {"edition_id": edition_id})

    async def publish_edition(self, edition_id: str) -> Dict[str, Any]:
        return await self._call("publish_edition", {"edition_id": edition_id})

    async def unpublish_edition(self, edition_id: str) -> Dict[str, Any]:
        return await self._call("unpublish_edition", {"edition_id": edition_id})

    submit_candidates = submit_candidate_stories
    stage_draft = stage_edition_draft

    async def record_editorial_override(
        self,
        edition_id: str,
        story_id: Optional[str] = None,
        override_type: str = "manual_override",
        rationale: str = "",
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self._call("record_editorial_override", {
            "edition_id": edition_id,
            "story_id": story_id,
            "override_type": override_type,
            "rationale": rationale,
            "previous_value": previous_value,
            "new_value": new_value,
        })


class EditorialMCPSyncClient:
    """Synchronous convenience wrapper around EditorialMCPClient."""
    def __init__(self, async_client: Optional[EditorialMCPClient] = None):
        self._async = async_client or EditorialMCPClient()

    def get_editorial_context(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.get_editorial_context(*args, **kwargs))

    def get_feedback_analytics(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.get_feedback_analytics(*args, **kwargs))

    def get_historical_feedback(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return asyncio.run(self._async.get_historical_feedback(*args, **kwargs))

    def fetch_editorial_memory(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return asyncio.run(self._async.fetch_editorial_memory(*args, **kwargs))

    def submit_candidate_stories(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.submit_candidate_stories(*args, **kwargs))

    def get_candidate_details(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.get_candidate_details(*args, **kwargs))

    def stage_edition_draft(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.stage_edition_draft(*args, **kwargs))

    def get_edition_status(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.get_edition_status(*args, **kwargs))

    def publish_edition(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.publish_edition(*args, **kwargs))

    def unpublish_edition(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.unpublish_edition(*args, **kwargs))

    submit_candidates = submit_candidate_stories
    stage_draft = stage_edition_draft

    def record_editorial_override(self, *args, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async.record_editorial_override(*args, **kwargs))
