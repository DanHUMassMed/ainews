"""Evaluation and scoring step for editorial candidates."""

from typing import List, Dict, Any, Optional
from backend.app.services.scoring import ScoringEngine


class EvaluationStep:
    """Evaluates each candidate against significance, novelty, evidence, saturation, and feedback bias."""

    def __init__(self, scoring_engine=None):
        self.scoring_engine = scoring_engine or ScoringEngine

    async def execute(self, dossiers: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        from agents.app.workflows.root_workflow import resolve_candidate_feedback_bias

        evaluated = []
        weights = context.get("scoring_weights", {})
        fb_analytics = context.get("feedback_analytics", {})

        thresholds = context.get("scoring_thresholds", {})
        min_select = thresholds.get("min_selection_threshold", 4.0)
        core_min_score = thresholds.get("core_min_score", 6.0)
        core_min_evi = thresholds.get("core_min_evidence", 7.0)
        exp_min_score = thresholds.get("exploratory_min_score", 5.0)
        exp_min_nov = thresholds.get("exploratory_min_novelty", 6.5)
        stale_backup_min = thresholds.get("stale_backup_min_score", 4.5)

        for idx, d in enumerate(dossiers):
            # Whitelist boost for Tier 1 primary lab announcements
            tier_bonus = 0.5 if d.get("tier") == "Tier 1" else 0.0

            sig = float(d.get("significance") if d.get("significance") is not None else (7.0 + (idx % 3) * 0.8 + tier_bonus))
            nov = float(d.get("novelty") if d.get("novelty") is not None else (6.5 + (idx % 4) * 0.7))
            evi = float(d.get("evidence") if d.get("evidence") is not None else (8.0 if d.get("tier") in ("Tier 1", "Tier 2") else 7.0))
            sat = float(d.get("saturation") if d.get("saturation") is not None else 3.0)

            fb_bias = resolve_candidate_feedback_bias(d, fb_analytics)
            composite = self.scoring_engine.compute_composite_score(sig, nov, evi, sat, feedback_bias=fb_bias, weights=weights)

            if d.get("is_stale_rejection") and composite >= stale_backup_min:
                tier = "Stale Backup"
            elif d.get("rejected_reason") or composite < min_select:
                tier = "Rejected"
            elif composite >= core_min_score and evi >= core_min_evi:
                tier = "Core"
            elif nov >= exp_min_nov and composite >= exp_min_score:
                tier = "Exploratory"
            else:
                tier = "Contrarian"

            evaluated.append({
                **d,
                "scores": {
                    "significance": sig,
                    "novelty": nov,
                    "evidence": evi,
                    "saturation": sat,
                    "feedback_bias": fb_bias,
                    "composite": composite,
                },
                "tier": tier,
                "score": composite,
            })
        return evaluated
