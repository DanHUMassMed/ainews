import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class CandidateScoreDetail(BaseModel):
    significance: float = Field(..., ge=0.0, le=10.0, description="1-10 technology/industry significance")
    novelty: float = Field(..., ge=0.0, le=10.0, description="1-10 novelty or under-reported development")
    evidence: float = Field(..., ge=0.0, le=10.0, description="1-10 primary source & evidence quality")
    saturation: float = Field(..., ge=0.0, le=10.0, description="1-10 mainstream saturation penalty")
    feedback_bias: float = Field(0.0, ge=-3.0, le=3.0, description="-3 to +3 bias from reader preference")
    composite: Optional[float] = None

class CandidateSubmitItem(BaseModel):
    url: str
    title: str
    raw_text: Optional[str] = None
    normalized_text: Optional[str] = None
    discovered_at: Optional[datetime] = None
    scores: CandidateScoreDetail
    selected: bool = False
    rejected_reason: Optional[str] = None
    cluster_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class CandidateBatchSubmitRequest(BaseModel):
    edition_date: Optional[str] = None
    run_id: Optional[str] = None
    clear_existing: bool = True
    candidates: List[CandidateSubmitItem]

class CandidateResponse(BaseModel):
    id: uuid.UUID
    edition_id: Optional[uuid.UUID] = None
    url: str
    title: str
    discovered_at: datetime
    significance_score: float
    novelty_score: float
    evidence_score: float
    saturation_score: float
    feedback_bias: float
    composite_score: float
    selected: bool
    rejected_reason: Optional[str] = None
    cluster_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
