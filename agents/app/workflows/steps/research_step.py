"""Research and verification step validating URLs, whitelists, and publication recency."""

from datetime import date, datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Callable
from backend.app.services.url_validator import URLValidatorService
from backend.app.services.whitelist import WhitelistService


class ResearchStep:
    """Validates URL reachability, whitelist status, canonical source links, and recency."""

    def __init__(self, category_inferrer: Optional[Callable] = None):
        self.category_inferrer = category_inferrer

    async def execute(self, leads: List[Dict[str, Any]], target_date: str = "") -> List[Dict[str, Any]]:
        urls_to_validate = [
            lead.get("url", "") for lead in leads
            if lead.get("url") and lead.get("source_type") not in ("rss_feed", "arxiv_api")
        ]
        validation_results = await URLValidatorService.validate_urls_batch(urls_to_validate)

        # Parse target date for 48h recency check
        ref_date = date.today()
        if target_date:
            try:
                ref_date = date.fromisoformat(target_date)
            except Exception:
                ref_date = date.today()
        earliest_allowed = ref_date - timedelta(days=2)

        dossiers = []
        for lead in leads:
            url = lead.get("url", "")
            source_type = lead.get("source_type", "web")
            wl_entry = WhitelistService.get_source_for_url(url)

            # RSS and ArXiv feeds were retrieved live with HTTP 200
            if source_type in ("rss_feed", "arxiv_api"):
                val_res = {"is_valid": True, "status_code": 200, "error": None}
            else:
                val_res = validation_results.get(url, {"is_valid": False, "status_code": 0, "error": "Unvalidated"})

            rejected_reason = lead.get("rejected_reason")

            # 1. URL 200 Status Validation
            if not rejected_reason and not val_res["is_valid"]:
                rejected_reason = f"Rejected: Primary source URL returned HTTP {val_res['status_code']} ({val_res['error']})"

            # 2. Recency / Published Date Validation
            pub_at_str = lead.get("published_at") or lead.get("published_date")
            pub_date = None
            if pub_at_str:
                try:
                    clean_dt = pub_at_str.replace("Z", "+00:00")
                    pub_dt = datetime.fromisoformat(clean_dt)
                    pub_date = pub_dt.date()
                except Exception:
                    pass

            is_stale_rejection = False
            if not rejected_reason and pub_date and pub_date < earliest_allowed:
                rejected_reason = f"Rejected: Story is stale (published {pub_date} is older than 48-hour lookback window relative to {ref_date})"
                is_stale_rejection = True

            # 3. Paywall / Secondary Discovery Handling
            is_secondary_scoop = wl_entry and wl_entry.ingestion_strategy == "secondary_discovery_only"

            if self.category_inferrer:
                inferred_cats = self.category_inferrer(
                    title=lead.get("title", ""),
                    text=lead.get("summary") or lead.get("snippet", ""),
                    default_cat=wl_entry.category if wl_entry else "",
                )
            else:
                from agents.app.workflows.root_workflow import infer_story_categories
                inferred_cats = infer_story_categories(
                    title=lead.get("title", ""),
                    text=lead.get("summary") or lead.get("snippet", ""),
                    default_cat=wl_entry.category if wl_entry else "",
                )

            dossier = {
                "is_stale_rejection": is_stale_rejection,
                "occurrence_date": str(pub_date) if pub_date else None,
                "title": lead.get("title", ""),
                "url": url,
                "raw_url": lead.get("raw_url", url),
                "summary": lead.get("summary") or lead.get("snippet", ""),
                "content": lead.get("content", ""),
                "image_url": lead.get("image_url"),
                "why_it_matters": lead.get("why_it_matters", ""),
                "publisher": lead.get("publisher", wl_entry.domain if wl_entry else "Web"),
                "tier": lead.get("tier", wl_entry.tier if wl_entry else "Tier 3"),
                "category_slugs": lead.get("category_slugs") or inferred_cats,
                "is_lead": lead.get("is_lead", False),
                "published_at": pub_at_str or datetime.now(timezone.utc).isoformat(),
                "significance": lead.get("significance"),
                "novelty": lead.get("novelty"),
                "evidence": lead.get("evidence"),
                "saturation": lead.get("saturation"),
                "rejected_reason": rejected_reason,
                "source_status_code": val_res.get("status_code", 200),
                "is_secondary_scoop": is_secondary_scoop,
            }
            dossiers.append(dossier)
        return dossiers
