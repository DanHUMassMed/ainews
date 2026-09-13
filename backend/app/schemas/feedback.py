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
    upvotes: int
    downvotes: int
    approval_rate: float

class EntityFeedbackItem(BaseModel):
    entity: str
    net_score: int
    bias_rating: float

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
