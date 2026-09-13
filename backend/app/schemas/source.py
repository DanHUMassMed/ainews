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
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                dt = parsedate_to_datetime(v)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                pass
            try:
                dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                return None
        return v

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
