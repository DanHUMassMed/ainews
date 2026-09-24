from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.configuration import EditorialConfiguration


DEFAULT_THRESHOLDS = {
    "min_selection_threshold": 4.0,
    "core_min_score": 6.0,
    "core_min_evidence": 7.0,
    "exploratory_min_score": 5.0,
    "exploratory_min_novelty": 6.5,
    "contrarian_min_novelty": 8.0,
    "contrarian_max_saturation": 4.0,
    "stale_backup_min_score": 4.5,
}

DEFAULT_WEIGHTS = {
    "significance_weight": 0.35,
    "novelty_weight": 0.25,
    "evidence_weight": 0.20,
    "saturation_weight": 0.20,
    "feedback_weight": 0.15,
}

def extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "web"
    except Exception:
        return "web"

class ScoringEngine:
    @staticmethod
    async def get_active_weights(session: AsyncSession, cold_start_active: bool = False) -> Dict[str, float]:
        res = await session.execute(
            select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_weights")
        )
        cfg = res.scalar_one_or_none()
        weights = DEFAULT_WEIGHTS.copy()
        if cfg and isinstance(cfg.value, dict):
            for k in weights.keys():
                if k in cfg.value:
                    weights[k] = float(cfg.value[k])

        if cold_start_active:
            weights["feedback_weight"] = 0.0
        return weights

    @staticmethod
    async def get_active_thresholds(session: AsyncSession) -> Dict[str, float]:
        res = await session.execute(
            select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_thresholds")
        )
        cfg = res.scalar_one_or_none()
        thresholds = DEFAULT_THRESHOLDS.copy()
        if cfg and isinstance(cfg.value, dict):
            for k in thresholds.keys():
                if k in cfg.value:
                    thresholds[k] = float(cfg.value[k])
        return thresholds


    @staticmethod
    def compute_composite_score(
        significance: float,
        novelty: float,
        evidence: float,
        saturation: float,
        feedback_bias: float = 0.0,
        weights: Dict[str, float] = None,
    ) -> float:
        if weights is None:
            weights = DEFAULT_WEIGHTS

        # Clamp bounds
        sig = max(1.0, min(10.0, float(significance)))
        nov = max(1.0, min(10.0, float(novelty)))
        evi = max(1.0, min(10.0, float(evidence)))
        sat = max(1.0, min(10.0, float(saturation)))
        fb = max(-3.0, min(3.0, float(feedback_bias)))

        # S = w1*Sig + w2*Nov + w3*Evi - w4*Sat + w5*FeedbackBias
        score = (
            weights.get("significance_weight", 0.35) * sig
            + weights.get("novelty_weight", 0.25) * nov
            + weights.get("evidence_weight", 0.20) * evi
            - weights.get("saturation_weight", 0.20) * sat
            + weights.get("feedback_weight", 0.15) * fb
        )
        return round(score, 3)

    @staticmethod
    def partition_portfolio(
        candidates: List[Dict[str, Any]],
        target_count: int = 8,
        max_per_domain: int = 1,
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        Applies 70% Core, 20% Exploratory, 10% Contrarian portfolio distribution.
        Enforces domain/source diversity (capping stories per domain).
        Handles low-signal days if qualified candidates < 5.
        """
        # Sort candidates by composite score descending
        sorted_candidates = sorted(candidates, key=lambda c: c.get("composite_score", 0.0), reverse=True)
        
        # Qualified candidates have score >= 4.0
        qualified = [c for c in sorted_candidates if c.get("composite_score", 0.0) >= 4.0]
        
        # Check low-signal threshold
        if len(qualified) < 5:
            low_signal_notice = (
                "Low-signal day across the industry. Highlighting only developments "
                "that appear to represent genuine shifts."
            )
            return qualified[:min(len(qualified), target_count)], True, low_signal_notice

        # Target allocations: ~70% core, ~20% exploratory, ~10% contrarian
        core_target = max(3, int(target_count * 0.70))
        exploratory_target = max(1, int(target_count * 0.20))
        contrarian_target = max(1, target_count - core_target - exploratory_target)

        selected = []
        domain_counts: Dict[str, int] = {}
        core_list = []
        exploratory_list = []
        contrarian_list = []

        for c in qualified:
            novelty = c.get("novelty_score", 5.0)
            saturation = c.get("saturation_score", 5.0)
            
            # Contrarian: high novelty (>=8), low saturation (<=4)
            if novelty >= 8.0 and saturation <= 4.0:
                contrarian_list.append(c)
            # Exploratory: novelty >= 6.5
            elif novelty >= 6.5:
                exploratory_list.append(c)
            else:
                core_list.append(c)

        def can_add(cand: Dict[str, Any], limit: int) -> bool:
            dom = extract_domain(cand.get("url", ""))
            return domain_counts.get(dom, 0) < limit

        def add_candidate(cand: Dict[str, Any]):
            selected.append(cand)
            dom = extract_domain(cand.get("url", ""))
            domain_counts[dom] = domain_counts.get(dom, 0) + 1

        # Pass 1: Strict domain limit (e.g. max 1 per domain)
        for pool, target in [(core_list, core_target), (exploratory_list, exploratory_target), (contrarian_list, contrarian_target)]:
            added = 0
            for c in pool:
                if c not in selected and can_add(c, max_per_domain) and added < target:
                    add_candidate(c)
                    added += 1

        # Pass 2: If slots remain, fill with any diverse qualified candidate
        if len(selected) < target_count:
            for c in qualified:
                if c not in selected and can_add(c, max_per_domain):
                    add_candidate(c)
                    if len(selected) >= target_count:
                        break

        # Pass 3: Relax domain limit if needed to reach target_count
        if len(selected) < target_count:
            for c in qualified:
                if c not in selected:
                    add_candidate(c)
                    if len(selected) >= target_count:
                        break

        return selected, False, ""
