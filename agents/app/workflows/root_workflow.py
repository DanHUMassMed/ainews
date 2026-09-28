"""Master Editorial Workflow Orchestrator for AI Industry News Daily.

Orchestrates the 6-agent Hermes pipeline:
1. Context & Feedback Initialization (via Editorial MCP)
2. Discovery (Whitelisted Feeds, ArXiv API, Reddit Pulse, SearXNG)
3. Research & Verification (Whitelist validation, canonical source attribution, recency)
4. Evaluation & Scoring (4-dimensional composite scoring + feedback bias)
5. Selection & Story Mix (Core, Exploratory, Contrarian balancing)
6. Writing & Synthesis (Why-It-Matters, anti-buzzword constraints)
7. Adversarial Critique & Publication Gate
8. Staging & Publishing (via Editorial MCP)
"""

import sys
import re
import html
import json
import uuid
import logging
import asyncio
from datetime import date, datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from agents.app.workflows.steps import (
    ContextStep,
    DiscoveryStep,
    ResearchStep,
    EvaluationStep,
    SelectionStep,
    WritingStep,
    CritiqueStep,
)
from agents.app.agents import (
    create_discovery_agent,
    create_research_agent,
    create_evaluation_agent,
    create_selection_agent,
    create_writing_agent,
    create_critic_agent,
    synthesize_story,
    sanitize_story_completeness,
)
from agents.app.tools.editorial_mcp_tool import (
    get_editorial_context,
    submit_candidate_stories,
    stage_edition_draft,
    get_edition_status,
    publish_edition,
    record_editorial_override,
)
from agents.app.tools.searxng_tool import run_discovery_matrix, search_web
from agents.app.tools.firecrawl_tool import scrape_webpage
from backend.app.services.scoring import ScoringEngine
from backend.app.services.url_validator import URLValidatorService
from backend.app.services.whitelist import WhitelistService
from backend.app.services.feed_ingestion import FeedIngestionService

from backend.app.utils.text import PROHIBITED_BUZZWORDS, slugify, strip_html
from backend.app.utils.dates import parse_datetime_flexible

logger = logging.getLogger("ainews.workflow")

@dataclass
class WorkflowResult:
    edition_id: Optional[str] = None
    target_date: str = ""
    status: str = "failed"
    candidate_count: int = 0
    story_count: int = 0
    low_signal: bool = False
    low_signal_notice: Optional[str] = None
    critic_passed: bool = False
    revisions_performed: int = 0
    errors: List[str] = field(default_factory=list)
    edition_payload: Optional[Dict[str, Any]] = None
    staged_draft: Optional[Dict[str, Any]] = None


def infer_story_categories(title: str, text: str = "", default_cat: str = "") -> List[str]:
    """Infers relevant category slugs for candidate stories based on technical taxonomy keywords with word boundaries."""
    from backend.app.core.taxonomy import get_category_keywords
    combined = f"{title} {text}".lower()
    categories = []

    def has_any(patterns: List[str]) -> bool:
        return any(re.search(r"\b" + re.escape(p) + r"\b", combined) for p in patterns)

    taxonomy_keywords = get_category_keywords()
    for cat_slug, patterns in taxonomy_keywords.items():
        if has_any(patterns):
            categories.append(cat_slug)

    if not categories:
        if default_cat and default_cat.lower() not in ("unknown", "general ai", "web"):
            categories.append(default_cat.lower().replace(" ", "-"))
        else:
            categories.append("ai-models")

    return list(dict.fromkeys(categories))


def resolve_candidate_feedback_bias(
    candidate: Dict[str, Any],
    feedback_analytics: Dict[str, Any],
    min_category_votes: int = 3,
) -> float:
    """
    Computes dynamic feedback bias [-3.0 to +3.0] for an incoming candidate story based on
    reader feedback on 'like' stories in matching categories or topics, prioritizing editorial overrides.
    """
    if not feedback_analytics:
        return 0.0

    cand_cats = [c.lower() for c in candidate.get("category_slugs", [])]
    if candidate.get("category"):
        cand_cats.append(candidate["category"].lower().replace(" ", "-"))

    cat_overrides = feedback_analytics.get("category_overrides", {})
    categories_data = feedback_analytics.get("categories", [])

    override_lookup = {}
    cat_lookup = {}

    for cat in categories_data:
        if isinstance(cat, dict):
            slug = str(cat.get("slug", "")).lower()
            name = str(cat.get("category_name", "")).lower().replace(" ", "-")
            up = int(cat.get("upvotes", 0))
            down = int(cat.get("downvotes", 0))
            rate = float(cat.get("approval_rate", 0.5))
            is_ovr = bool(cat.get("override_active", False))
            ovr_bias = cat.get("override_bias")
        else:
            slug = str(getattr(cat, "slug", "")).lower()
            name = str(getattr(cat, "category_name", "")).lower().replace(" ", "-")
            up = int(getattr(cat, "upvotes", 0))
            down = int(getattr(cat, "downvotes", 0))
            rate = float(getattr(cat, "approval_rate", 0.5))
            is_ovr = bool(getattr(cat, "override_active", False))
            ovr_bias = getattr(cat, "override_bias", None)

        if is_ovr and ovr_bias is not None:
            if slug:
                override_lookup[slug] = float(ovr_bias)
            if name:
                override_lookup[name] = float(ovr_bias)

        total_cat_votes = up + down
        if total_cat_votes >= min_category_votes:
            if slug:
                cat_lookup[slug] = rate
            if name:
                cat_lookup[name] = rate

    if isinstance(cat_overrides, dict):
        for o_slug, o_val in cat_overrides.items():
            if isinstance(o_val, dict) and o_val.get("active", False):
                override_lookup[str(o_slug).lower()] = float(o_val.get("manual_bias", 0.0))

    matched_overrides = [override_lookup[c] for c in cand_cats if c in override_lookup]
    if matched_overrides:
        avg_ovr = sum(matched_overrides) / len(matched_overrides)
        return round(max(-3.0, min(3.0, avg_ovr)), 3)

    matched_rates = [cat_lookup[c] for c in cand_cats if c in cat_lookup]

    if not matched_rates:
        text = f"{candidate.get('title', '')} {candidate.get('summary', '')}".lower()
        pos_topics = [str(t).lower() for t in feedback_analytics.get("top_positive_topics", [])]
        neg_topics = [str(t).lower() for t in feedback_analytics.get("top_negative_topics", [])]
        for p in pos_topics:
            if p in text or any(p in c for c in cand_cats):
                matched_rates.append(0.80)
        for n in neg_topics:
            if n in text or any(n in c for c in cand_cats):
                matched_rates.append(0.20)

    if not matched_rates:
        return 0.0

    avg_rate = sum(matched_rates) / len(matched_rates)
    raw_bias = 6.0 * (avg_rate - 0.50)
    return round(max(-3.0, min(3.0, raw_bias)), 3)


class EditorialWorkflow:
    def __init__(
        self,
        live: bool = False,
        max_revisions: int = 2,
        context_step: Optional[ContextStep] = None,
        discovery_step: Optional[DiscoveryStep] = None,
        research_step: Optional[ResearchStep] = None,
        evaluation_step: Optional[EvaluationStep] = None,
        selection_step: Optional[SelectionStep] = None,
        writing_step: Optional[WritingStep] = None,
        critique_step: Optional[CritiqueStep] = None,
    ):
        self.live = live
        self.max_revisions = max_revisions
        self.run_id = str(uuid.uuid4())
        self.context_step = context_step or ContextStep()
        self.discovery_step = discovery_step or DiscoveryStep(live=live)
        self.research_step = research_step or ResearchStep(category_inferrer=infer_story_categories)
        self.evaluation_step = evaluation_step or EvaluationStep()
        self.selection_step = selection_step or SelectionStep(live=live)
        self.writing_step = writing_step or WritingStep(live=live)
        self.critique_step = critique_step or CritiqueStep(max_revisions=max_revisions)

    async def run(
        self,
        target_date: Optional[str] = None,
        sample_candidates: Optional[List[Dict[str, Any]]] = None,
        publish: bool = False
    ) -> WorkflowResult:
        """Executes the end-to-end editorial pipeline."""
        t_date = target_date or date.today().isoformat()
        result = WorkflowResult(target_date=t_date)

        try:
            # 1. Initialize Context & Memory via MCP
            context = await self.step_initialize_context()

            # 2. Discovery Phase (Whitelisted feeds, APIs, SearXNG)
            raw_leads = await self.step_discovery(sample_candidates=sample_candidates)
            result.candidate_count = len(raw_leads)

            # 3. Research Phase (Validation, whitelist verification, recency)
            dossiers = await self.step_research(raw_leads, target_date=t_date)

            # 4. Evaluation Phase (Scoring)
            evaluated_candidates = await self.step_evaluation(dossiers, context)

            # 5. Selection Phase (Story Mix, Low-Signal Gate & Backup Opportunity Recovery)
            selected_stories, low_signal_notice = await self.step_selection(evaluated_candidates, context=context)
            result.low_signal = low_signal_notice is not None

            # Mark selected flags and metadata on evaluated_candidates for DB audit trail
            selected_urls = {s["url"] for s in selected_stories}
            for c in evaluated_candidates:
                c["selected"] = c["url"] in selected_urls
                if not c.get("metadata_json"):
                    c["metadata_json"] = {}
                c["metadata_json"]["edition_date"] = t_date
                c["metadata_json"]["recovered_from_backup"] = c.get("recovered_from_backup", False)
                c["metadata_json"]["published_at"] = c.get("published_at")
                c["metadata_json"]["occurrence_date"] = c.get("occurrence_date")

            # Ingest candidates into DB via Editorial MCP (clearing prior run clutter)
            await submit_candidate_stories(
                evaluated_candidates,
                run_id=self.run_id,
                clear_existing=True,
                edition_date=t_date,
            )

            # 6. Writing Phase (Synthesize Briefings)
            written_stories = await self.step_writing(selected_stories)

            # 7. Critic & Publication Gate Audit
            final_stories, passed_gate, revisions = await self.step_critique_and_revision(
                written_stories, dossiers, low_signal_notice
            )
            result.critic_passed = passed_gate
            result.revisions_performed = revisions
            result.story_count = len(final_stories)

            if not passed_gate:
                result.status = "critic_rejected"
                result.errors.append("Publication gate rejected edition due to uncorrected quality violations.")
                return result

            # 8. Staging & Publishing Phase
            staged = await stage_edition_draft(
                date=t_date,
                title=f"AI Industry Briefing — {t_date}",
                introduction=f"Curated analysis of the most consequential frontier model, open-weights, and infrastructure developments for {t_date}.",
                low_signal_notice=low_signal_notice,
                stories=final_stories,
            )
            edition_id = staged.get("edition_id") or staged.get("id")
            result.edition_id = edition_id

            if publish and edition_id:
                pub_res = await publish_edition(edition_id)
                result.status = pub_res.get("status", "published")
            else:
                result.status = "staged_draft"

            result.low_signal = (low_signal_notice is not None)
            result.low_signal_notice = low_signal_notice
            result.staged_draft = staged
            result.edition_payload = staged
            return result

        except Exception as e:
            logger.error(f"Editorial workflow fatal error: {e}", exc_info=True)
            result.status = "error"
            result.errors.append(str(e))
            return result

    async def step_initialize_context(self) -> Dict[str, Any]:
        """Fetch editorial context, scoring weights, guidelines, and feedback analytics."""
        return await self.context_step.execute()

    async def step_discovery(self, sample_candidates: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Discover candidate leads from whitelisted feeds, ArXiv, Reddit, and SearXNG."""
        return await self.discovery_step.execute(sample_candidates)

    async def step_research(self, leads: List[Dict[str, Any]], target_date: str = "") -> List[Dict[str, Any]]:
        """Validate URL reachability, whitelist status, canonical source links, and recency."""
        return await self.research_step.execute(leads, target_date=target_date)

    async def step_evaluation(self, dossiers: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate each dossier against the 4 core dimensions + feedback bias."""
        return await self.evaluation_step.execute(dossiers, context)

    async def step_selection(
        self,
        evaluated_candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Selection Phase (Selection Agent): Reviews entire newsletter layout as a single document."""
        return await self.selection_step.execute(evaluated_candidates, context=context)

    async def _synthesize_candidate(self, c: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Synthesizes a publication-grade newspaper story using the Writing Agent with self-review."""
        return await self.writing_step.synthesize_candidate(c, idx)

    async def step_writing(self, selected_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesize candidate stories into publication-grade briefing items."""
        return await self.writing_step.execute(selected_candidates)

    async def step_critique_and_revision(
        self,
        stories: List[Dict[str, Any]],
        dossiers: List[Dict[str, Any]],
        low_signal_notice: Optional[str]
    ) -> tuple[List[Dict[str, Any]], bool, int]:
        """Adversarial audit and revision loop enforcing Publication Gate compliance."""
        return await self.critique_step.execute(stories, dossiers, low_signal_notice)
