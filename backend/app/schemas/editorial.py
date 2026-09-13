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
    feedback_analytics: FeedbackAnalyticsResponse
    repetition_avoid_topics: List[str] = []
    portfolio_targets: Dict[str, int] = {"core": 70, "exploratory": 20, "contrarian": 10}
