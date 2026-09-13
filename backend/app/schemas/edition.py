import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.story import StoryResponse, StoryCreate

class EditionBase(BaseModel):
    date: date
    title: str
    introduction: str = ""
    low_signal_notice: Optional[str] = None

class EditionCreate(EditionBase):
    pass

class EditionDraftStageRequest(EditionBase):
    run_id: Optional[str] = None
    stories: List[StoryCreate]

class EditionResponse(EditionBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    story_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class EditionDetailResponse(EditionResponse):
    stories: List[StoryResponse] = []
    lead_story: Optional[StoryResponse] = None

class EditionStatusResponse(BaseModel):
    id: uuid.UUID
    date: date
    status: str
    story_count: int
    is_valid: bool
    validation_errors: List[str] = []
    published_at: Optional[datetime] = None
