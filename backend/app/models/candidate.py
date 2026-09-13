import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class StoryCandidate(Base):
    __tablename__ = "story_candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    edition_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("editions.id", ondelete="SET NULL"), nullable=True, index=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    normalized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    # 5 Scoring Dimensions
    significance_score: Mapped[float] = mapped_column(Float, default=0.0) # 1-10
    novelty_score: Mapped[float] = mapped_column(Float, default=0.0)      # 1-10
    evidence_score: Mapped[float] = mapped_column(Float, default=0.0)     # 1-10
    saturation_score: Mapped[float] = mapped_column(Float, default=0.0)   # 1-10
    feedback_bias: Mapped[float] = mapped_column(Float, default=0.0)      # -3 to +3
    composite_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    selected: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rejected_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cluster_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    edition: Mapped[Optional["Edition"]] = relationship("Edition", back_populates="candidates")
    sources: Mapped[List["Source"]] = relationship("Source", back_populates="candidate")
