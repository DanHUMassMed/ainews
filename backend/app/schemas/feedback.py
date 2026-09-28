import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class FeedbackSubmitRequest(BaseModel):
    story_id: uuid.UUID
    vote: int = Field(..., description="+1 for thumbs up, -1 for thumbs down")
    session_id: str = Field(..., min_length=1, max_length=255)

class FeedbackResponse(BaseModel):
    status: str
    story_id: uuid.UUID
    vote: int
    upvotes: int
    downvotes: int

class CategoryFeedbackItem(BaseModel):
    category_name: str
    slug: str
    upvotes: int = 0
    downvotes: int = 0
    total_votes: int = 0
    approval_rate: float = 0.50
    raw_bias: float = 0.0
    override_active: bool = False
    override_bias: Optional[float] = None
    effective_bias: float = 0.0
    override_reason: Optional[str] = None

class EntityFeedbackItem(BaseModel):
    entity: str
    net_score: int
    bias_rating: float

class CategoryOverrideRequest(BaseModel):
    slug: str
    manual_bias: float = Field(..., ge=-3.0, le=3.0, description="Manual editorial bias between -3.0 and +3.0")
    active: bool = True
    reason: Optional[str] = Field(default="", description="Editorial rationale for the override")

class FeedbackVoteUpdateRequest(BaseModel):
    vote: int = Field(..., description="+1 or -1")

class FeedbackAnalyticsResponse(BaseModel):
    window_days: int
    total_votes: int
    total_upvotes: int
    total_downvotes: int
    overall_approval_rate: float
    cold_start_active: bool
    categories: List[CategoryFeedbackItem] = []
    top_positive_topics: List[str] = []
    top_negative_topics: List[str] = []
    category_overrides: Dict[str, Any] = {}
