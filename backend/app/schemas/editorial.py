import uuid
from datetime import date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from backend.app.schemas.feedback import FeedbackAnalyticsResponse

class ScoringWeightsConfig(BaseModel):
    significance_weight: float = 0.35
    novelty_weight: float = 0.25
    evidence_weight: float = 0.20
    saturation_weight: float = 0.20
    feedback_weight: float = 0.15

class ScoringThresholdsConfig(BaseModel):
    min_selection_threshold: float = 4.0
    core_min_score: float = 6.0
    core_min_evidence: float = 7.0
    exploratory_min_score: float = 5.0
    exploratory_min_novelty: float = 6.5
    contrarian_min_novelty: float = 8.0
    contrarian_max_saturation: float = 4.0
    stale_backup_min_score: float = 4.5

class ScoringConfigResponse(BaseModel):
    weights: ScoringWeightsConfig
    thresholds: ScoringThresholdsConfig
    description: Optional[str] = None
    updated_at: Optional[str] = None

class ScoringConfigUpdateRequest(BaseModel):
    weights: Optional[ScoringWeightsConfig] = None
    thresholds: Optional[ScoringThresholdsConfig] = None

class RecentStoryContextItem(BaseModel):
    title: str
    slug: str
    date: date
    categories: List[str] = []
    why_it_matters: str
    primary_source: Optional[str] = None

class EntityFrequencyItem(BaseModel):
    entity: str
    frequency_count: int
    repetition_warning: bool

class EditorialContextRequest(BaseModel):
    days_lookback: int = 28

class EditorialContextResponse(BaseModel):
    publication_date: date
    lookback_days: int
    recent_stories: List[RecentStoryContextItem] = []
    recent_covered_entities: List[EntityFrequencyItem] = []
    scoring_weights: ScoringWeightsConfig
    scoring_thresholds: Optional[ScoringThresholdsConfig] = None
    feedback_analytics: FeedbackAnalyticsResponse
    repetition_avoid_topics: List[str] = []
    portfolio_targets: Dict[str, int] = {"core": 70, "exploratory": 20, "contrarian": 10}
