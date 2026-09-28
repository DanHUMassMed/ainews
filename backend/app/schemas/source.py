import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

class SourceBase(BaseModel):
    url: str
    title: Optional[str] = None
    publisher: Optional[str] = None
    published_at: Optional[datetime] = None
    source_type: Optional[str] = None

    @field_validator("published_at", mode="before")
    @classmethod
    def parse_datetime_flexible(cls, v):
        from backend.app.utils.dates import parse_datetime_flexible as _parse_dt
        return _parse_dt(v)
        return v

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
