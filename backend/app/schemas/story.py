import uuid
import re
import html
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from backend.app.schemas.source import SourceBase, SourceResponse
from backend.app.schemas.category import CategoryResponse

def _strip_html(v: Optional[str]) -> Optional[str]:
    if not v or not isinstance(v, str):
        return v
    # Unpack CDATA first
    t = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", v)
    t = html.unescape(t)
    t = html.unescape(t)
    t = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", t, flags=re.IGNORECASE)
    t = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", t, flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return " ".join(t.split()).strip()

class StoryBase(BaseModel):
    slug: Optional[str] = None
    title: str
    summary: str
    body: str = ""
    why_it_matters: str
    image_url: Optional[str] = None
    is_lead: bool = False
    position: int = 0
    published_at: Optional[datetime] = None

    @field_validator("title", "summary", "why_it_matters", mode="before")
    @classmethod
    def clean_text_fields(cls, v):
        return _strip_html(v) if isinstance(v, str) else v

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

class StoryCreate(StoryBase):
    sources: List[SourceBase] = []
    category_slugs: List[str] = []

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    body: Optional[str] = None
    why_it_matters: Optional[str] = None
    image_url: Optional[str] = None
    is_lead: Optional[bool] = None
    position: Optional[int] = None
    status: Optional[str] = None
    category_slugs: Optional[List[str]] = None

class StoryResponse(StoryBase):
    id: uuid.UUID
    edition_id: uuid.UUID
    slug: str
    status: str
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    sources: List[SourceResponse] = []
    categories: List[CategoryResponse] = []

    model_config = ConfigDict(from_attributes=True)
