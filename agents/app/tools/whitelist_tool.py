"""ADK Tool for Whitelist Domain Verification & Ingestion Strategy."""

from typing import Dict, Any, List, Optional
from backend.app.services.whitelist import WhitelistService

def check_whitelist_status(url: str) -> Dict[str, Any]:
    """Validates whether an article URL belongs to a vetted whitelist publication.

    Args:
        url: The web URL to inspect.

    Returns:
        Dict with is_whitelisted, tier, category, ingestion_strategy, and scoping_advice.
    """
    entry = WhitelistService.get_source_for_url(url)
    if not entry:
        return {
            "url": url,
            "is_whitelisted": False,
            "tier": "Unlisted",
            "category": "Unknown",
            "ingestion_strategy": "unvetted",
            "pipeline_action": "Requires corroboration",
            "scoping_advice": "Domain is not on the vetted whitelist.",
        }

    return {
        "url": url,
        "is_whitelisted": True,
        "tier": entry.tier,
        "category": entry.category,
        "ingestion_strategy": entry.ingestion_strategy,
        "pipeline_action": entry.pipeline_action,
        "scoping_advice": entry.scoping_advice,
        "active_feed": entry.active_feed,
        "is_paywall": entry.is_paywall,
    }

def get_whitelisted_sources(tier: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns list of vetted whitelist sources, optionally filtered by tier."""
    sources = WhitelistService.get_all_sources()
    if tier:
        sources = [s for s in sources if s.tier.lower() == tier.lower()]
    return [s.model_dump() for s in sources]
