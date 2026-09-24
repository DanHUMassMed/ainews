import uuid
import re
from datetime import date, datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from sqlalchemy.orm import selectinload

from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import verify_editorial_token
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.models.source import Source
from backend.app.models.category import Category
from backend.app.models.candidate import StoryCandidate
from backend.app.models.feedback import Feedback
from backend.app.models.memory import EditorialMemory
from backend.app.models.pipeline_run import PipelineRun
from backend.app.models.configuration import EditorialConfiguration
from backend.app.schemas.editorial import (
    EditorialContextRequest,
    EditorialContextResponse,
    ScoringWeightsConfig,
    ScoringThresholdsConfig,
    ScoringConfigResponse,
    ScoringConfigUpdateRequest,
)
from backend.app.schemas.feedback import FeedbackAnalyticsResponse
from backend.app.schemas.candidate import (
    CandidateBatchSubmitRequest,
    CandidateResponse,
)
from backend.app.schemas.edition import (
    EditionDraftStageRequest,
    EditionResponse,
    EditionStatusResponse,
)
from backend.app.services.scoring import ScoringEngine, DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS
from backend.app.services.feedback import FeedbackService
from backend.app.services.editorial_memory import EditorialMemoryService

router = APIRouter(prefix="/editorial", tags=["Hermes Editorial Skill API"])

class AdminAuthRequest(BaseModel):
    password: str

@router.post("/auth", response_model=Dict[str, Any])
async def verify_admin_auth(req: AdminAuthRequest):
    """Verify admin password to unlock Editorial Admin & Pipeline."""
    if req.password == settings.EDITORIAL_ADMIN_PASSWORD:
        return {
            "status": "authenticated",
            "token": settings.EDITORIAL_SECRET_KEY,
            "message": "Access granted to Editorial Admin & Pipeline.",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password. Access denied.",
    )

def slugify(text: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
    return re.sub(r'[\s-]+', '-', slug).strip('-')[:100]

@router.post("/context", response_model=EditorialContextResponse)
async def get_editorial_context(
    req: EditorialContextRequest = EditorialContextRequest(),
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    return await EditorialMemoryService.get_editorial_context(db, days_lookback=req.days_lookback)

@router.get("/feedback-analytics", response_model=FeedbackAnalyticsResponse)
async def get_feedback_analytics(
    window_days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    return await FeedbackService.get_analytics(db, window_days=window_days)

@router.post("/candidates", response_model=Dict[str, Any])
async def submit_candidate_stories(
    req: CandidateBatchSubmitRequest,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    from sqlalchemy import delete
    if req.clear_existing:
        await db.execute(delete(StoryCandidate))

    cold_start = await FeedbackService.is_cold_start_active(db)
    weights = await ScoringEngine.get_active_weights(db, cold_start_active=cold_start)

    count_saved = 0
    for item in req.candidates:
        composite = item.scores.composite
        if composite is None:
            composite = ScoringEngine.compute_composite_score(
                significance=item.scores.significance,
                novelty=item.scores.novelty,
                evidence=item.scores.evidence,
                saturation=item.scores.saturation,
                feedback_bias=item.scores.feedback_bias,
                weights=weights,
            )

        candidate = StoryCandidate(
            url=item.url,
            title=item.title,
            raw_text=item.raw_text,
            normalized_text=item.normalized_text,
            discovered_at=item.discovered_at or datetime.now(timezone.utc),
            significance_score=item.scores.significance,
            novelty_score=item.scores.novelty,
            evidence_score=item.scores.evidence,
            saturation_score=item.scores.saturation,
            feedback_bias=item.scores.feedback_bias,
            composite_score=composite,
            selected=item.selected,
            rejected_reason=item.rejected_reason,
            cluster_id=item.cluster_id,
            metadata_json=item.metadata_json,
        )
        db.add(candidate)
        count_saved += 1

    await db.commit()
    return {
        "status": "success",
        "candidates_saved": count_saved,
        "run_id": req.run_id,
    }

@router.get("/candidates", response_model=List[CandidateResponse])
async def list_candidates(
    limit: int = 100,
    selected_only: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    stmt = (
        select(StoryCandidate)
        .order_by(StoryCandidate.selected.desc(), StoryCandidate.composite_score.desc(), StoryCandidate.discovered_at.desc())
        .limit(limit)
    )
    if selected_only is not None:
        stmt = stmt.where(StoryCandidate.selected == selected_only)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.delete("/candidates", response_model=Dict[str, Any])
async def clear_candidates(
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    from sqlalchemy import delete
    await db.execute(delete(StoryCandidate))
    await db.commit()
    return {"status": "cleared", "message": "Candidate audit records cleared successfully."}

@router.post("/draft", response_model=EditionResponse)
async def stage_edition_draft(
    draft: EditionDraftStageRequest,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    # Idempotent: check if edition for date exists
    res = await db.execute(
        select(Edition)
        .where(Edition.date == draft.date)
        .options(selectinload(Edition.stories).selectinload(Story.sources))
    )
    edition = res.scalar_one_or_none()
    if not edition:
        edition = Edition(
            date=draft.date,
            title=draft.title,
            introduction=draft.introduction,
            status="draft",
            low_signal_notice=draft.low_signal_notice,
        )
        db.add(edition)
        await db.flush()
    else:
        # Update metadata
        edition.title = draft.title
        edition.introduction = draft.introduction
        edition.low_signal_notice = draft.low_signal_notice
        # Remove existing stories if re-staging draft
        edition.status = "draft"
        for s in list(edition.stories):
            await db.delete(s)
        await db.flush()

    # Load categories for slug mapping
    cat_res = await db.execute(select(Category))
    categories_by_slug = {c.slug: c for c in cat_res.scalars().all()}

    # Add stories
    for idx, s_data in enumerate(draft.stories):
        slug = s_data.slug or slugify(s_data.title)
        story = Story(
            edition_id=edition.id,
            slug=slug,
            title=s_data.title,
            summary=s_data.summary,
            body=s_data.body,
            why_it_matters=s_data.why_it_matters,
            image_url=s_data.image_url,
            status="draft",
            is_lead=s_data.is_lead or (idx == 0 and not any(s.is_lead for s in draft.stories)),
            position=s_data.position or idx,
            published_at=s_data.published_at or datetime.now(timezone.utc),
        )
        # Attach categories
        for c_slug in s_data.category_slugs:
            if c_slug in categories_by_slug:
                story.categories.append(categories_by_slug[c_slug])

        # Attach sources
        for src in s_data.sources:
            source = Source(
                story=story,
                url=src.url,
                title=src.title,
                publisher=src.publisher,
                published_at=src.published_at,
                source_type=src.source_type,
            )
            db.add(source)

        db.add(story)

    await db.commit()
    await db.refresh(edition)

    count_res = await db.execute(select(func.count(Story.id)).where(Story.edition_id == edition.id))
    story_count = count_res.scalar() or 0

    return EditionResponse(
        id=edition.id,
        date=edition.date,
        title=edition.title,
        introduction=edition.introduction,
        status=edition.status,
        low_signal_notice=edition.low_signal_notice,
        created_at=edition.created_at,
        updated_at=edition.updated_at,
        published_at=edition.published_at,
        story_count=story_count,
    )

@router.get("/edition/{edition_id}/status", response_model=EditionStatusResponse)
async def get_edition_status(
    edition_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    stmt = (
        select(Edition)
        .where(Edition.id == edition_id)
        .options(selectinload(Edition.stories).selectinload(Story.sources))
    )
    res = await db.execute(stmt)
    edition = res.scalar_one_or_none()
    if not edition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edition not found")

    errors = []
    # Structural validation rules (PRD Section 36)
    if not edition.stories:
        errors.append("Edition has no stories staged.")
    
    # Story count check
    if not edition.low_signal_notice and len(edition.stories) < 5:
        errors.append(f"Requires at least 5 stories (has {len(edition.stories)}) unless marked low_signal.")

    # Lead story check
    lead_count = sum(1 for s in edition.stories if s.is_lead)
    if lead_count == 0:
        errors.append("No lead story selected.")
    elif lead_count > 1:
        errors.append("Multiple lead stories selected.")

    # Story content & formatting checks
    import re
    html_pattern = re.compile(r"<[a-zA-Z/][^>]*>")
    slugs = set()
    for s in edition.stories:
        if not s.title or len(s.title.strip()) < 15:
            errors.append(f"Story '{s.title}' headline too short (min 15 chars).")
        if not s.summary or len(s.summary.strip()) < 150:
            errors.append(f"Story '{s.title}' summary too short (has {len(s.summary.strip())} chars, min 150 required).")
        if not s.why_it_matters or len(s.why_it_matters.strip()) < 60:
            errors.append(f"Story '{s.title}' missing substantive 'Why It Matters' (min 60 chars).")
        if not s.body or len(s.body.strip()) < 400:
            errors.append(f"Story '{s.title}' technical deep-dive body too short (min 400 chars).")
        if "analysis of recent advances in" in s.summary.lower():
            errors.append(f"Story '{s.title}' contains generic placeholder summary.")
        if html_pattern.search(s.summary) or html_pattern.search(s.why_it_matters) or html_pattern.search(s.title):
            errors.append(f"Story '{s.title}' contains raw HTML tags.")
        if not s.sources:
            errors.append(f"Story '{s.title}' missing required source URL.")
        if s.slug in slugs:
            errors.append(f"Duplicate story slug '{s.slug}'.")
        slugs.add(s.slug)

    return EditionStatusResponse(
        id=edition.id,
        date=edition.date,
        status=edition.status,
        story_count=len(edition.stories),
        is_valid=len(errors) == 0,
        validation_errors=errors,
        published_at=edition.published_at,
    )

@router.post("/edition/{edition_id}/publish", response_model=EditionResponse)
async def publish_edition(
    edition_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    status_check = await get_edition_status(edition_id=edition_id, db=db, _token=_token)
    if not status_check.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Edition failed publication gate: {', '.join(status_check.validation_errors)}"
        )

    res = await db.execute(
        select(Edition)
        .where(Edition.id == edition_id)
        .options(selectinload(Edition.stories))
    )
    edition = res.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    edition.status = "published"
    edition.published_at = now
    for s in edition.stories:
        s.status = "published"
        s.published_at = now

    await db.commit()
    await db.refresh(edition)

    return EditionResponse(
        id=edition.id,
        date=edition.date,
        title=edition.title,
        introduction=edition.introduction,
        status=edition.status,
        low_signal_notice=edition.low_signal_notice,
        created_at=edition.created_at,
        updated_at=edition.updated_at,
        published_at=edition.published_at,
        story_count=len(edition.stories),
    )

@router.post("/edition/{edition_id}/unpublish", response_model=EditionResponse)
async def unpublish_edition(
    edition_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    res = await db.execute(
        select(Edition)
        .where(Edition.id == edition_id)
        .options(selectinload(Edition.stories))
    )
    edition = res.scalar_one_or_none()
    if not edition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edition not found")

    edition.status = "draft"
    for s in edition.stories:
        s.status = "draft"

    await db.commit()
    await db.refresh(edition)
    return EditionResponse(
        id=edition.id,
        date=edition.date,
        title=edition.title,
        introduction=edition.introduction,
        status=edition.status,
        low_signal_notice=edition.low_signal_notice,
        created_at=edition.created_at,
        updated_at=edition.updated_at,
        published_at=edition.published_at,
        story_count=len(edition.stories),
    )


@router.get("/candidates/{candidate_id}", response_model=Dict[str, Any])
async def get_candidate_details(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    res = await db.execute(select(StoryCandidate).where(StoryCandidate.id == candidate_id))
    cand = res.scalar_one_or_none()
    if not cand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return {
        "id": str(cand.id),
        "url": cand.url,
        "title": cand.title,
        "raw_text": cand.raw_text,
        "normalized_text": cand.normalized_text,
        "discovered_at": cand.discovered_at.isoformat() if cand.discovered_at else None,
        "significance_score": cand.significance_score,
        "novelty_score": cand.novelty_score,
        "evidence_score": cand.evidence_score,
        "saturation_score": cand.saturation_score,
        "feedback_bias": cand.feedback_bias,
        "composite_score": cand.composite_score,
        "selected": cand.selected,
        "rejected_reason": cand.rejected_reason,
        "cluster_id": cand.cluster_id,
        "created_at": cand.created_at.isoformat() if cand.created_at else None,
    }

@router.get("/feedback-history", response_model=List[Dict[str, Any]])
async def get_feedback_history(
    limit: int = Query(50, ge=1, le=500),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = (
        select(Feedback)
        .where(Feedback.created_at >= cutoff)
        .order_by(desc(Feedback.created_at))
        .limit(limit)
        .options(selectinload(Feedback.story).selectinload(Story.categories))
    )
    res = await db.execute(stmt)
    records = []
    for f in res.scalars().all():
        records.append({
            "id": str(f.id),
            "story_id": str(f.story_id),
            "story_title": f.story.title if f.story else None,
            "vote": f.vote,
            "session_id": f.session_id,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "categories": [c.name for c in f.story.categories] if f.story else [],
        })
    return records

@router.get("/memory", response_model=List[Dict[str, Any]])
async def get_editorial_memory(
    memory_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    stmt = select(EditorialMemory)
    if memory_type:
        stmt = stmt.where(EditorialMemory.memory_type == memory_type)
    stmt = stmt.order_by(desc(EditorialMemory.updated_at)).limit(100)
    res = await db.execute(stmt)
    return [
        {
            "id": str(m.id),
            "memory_type": m.memory_type,
            "key": m.key,
            "payload": m.payload,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }
        for m in res.scalars().all()
    ]

@router.post("/override", response_model=Dict[str, Any])
async def record_editorial_override(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    override_id = uuid.uuid4()
    key = f"override_{override_id}"
    mem = EditorialMemory(
        id=override_id,
        memory_type="editorial_override",
        key=key,
        payload=payload,
    )
    db.add(mem)
    await db.commit()
    return {
        "status": "recorded",
        "override_id": str(override_id),
        "payload": payload,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/config/scoring", response_model=ScoringConfigResponse)
async def get_scoring_config(
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    """Retrieve active editorial scoring weights and quality thresholds."""
    w_res = await db.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_weights"))
    w_cfg = w_res.scalar_one_or_none()
    weights_dict = DEFAULT_WEIGHTS.copy()
    if w_cfg and isinstance(w_cfg.value, dict):
        weights_dict.update({k: float(v) for k, v in w_cfg.value.items() if k in weights_dict})

    t_res = await db.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_thresholds"))
    t_cfg = t_res.scalar_one_or_none()
    thresholds_dict = DEFAULT_THRESHOLDS.copy()
    if t_cfg and isinstance(t_cfg.value, dict):
        thresholds_dict.update({k: float(v) for k, v in t_cfg.value.items() if k in thresholds_dict})

    updated_at = None
    if w_cfg and w_cfg.updated_at:
        updated_at = w_cfg.updated_at.isoformat()

    return ScoringConfigResponse(
        weights=ScoringWeightsConfig(**weights_dict),
        thresholds=ScoringThresholdsConfig(**thresholds_dict),
        description=w_cfg.description if w_cfg else "Active multi-factor scoring configuration",
        updated_at=updated_at,
    )

@router.put("/config/scoring", response_model=ScoringConfigResponse)
async def update_scoring_config(
    req: ScoringConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    """Update active editorial scoring weights and thresholds in database."""
    now = datetime.now(timezone.utc)
    if req.weights:
        w_res = await db.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_weights"))
        w_cfg = w_res.scalar_one_or_none()
        w_dict = req.weights.model_dump()
        if not w_cfg:
            w_cfg = EditorialConfiguration(
                key="scoring_weights",
                value=w_dict,
                description="Custom weights for candidate composite scoring calculation",
                updated_at=now,
            )
            db.add(w_cfg)
        else:
            w_cfg.value = w_dict
            w_cfg.updated_at = now

    if req.thresholds:
        t_res = await db.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_thresholds"))
        t_cfg = t_res.scalar_one_or_none()
        t_dict = req.thresholds.model_dump()
        if not t_cfg:
            t_cfg = EditorialConfiguration(
                key="scoring_thresholds",
                value=t_dict,
                description="Custom selection and tier thresholds",
                updated_at=now,
            )
            db.add(t_cfg)
        else:
            t_cfg.value = t_dict
            t_cfg.updated_at = now

    await db.commit()
    return await get_scoring_config(db=db, _token=_token)

@router.post("/config/scoring/reset", response_model=ScoringConfigResponse)
async def reset_scoring_config(
    db: AsyncSession = Depends(get_db),
    _token: str = Security(verify_editorial_token),
):
    """Reset editorial scoring weights and thresholds to default canonical values."""
    now = datetime.now(timezone.utc)
    w_res = await db.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_weights"))
    w_cfg = w_res.scalar_one_or_none()
    if w_cfg:
        w_cfg.value = DEFAULT_WEIGHTS.copy()
        w_cfg.updated_at = now

    t_res = await db.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == "scoring_thresholds"))
    t_cfg = t_res.scalar_one_or_none()
    if t_cfg:
        t_cfg.value = DEFAULT_THRESHOLDS.copy()
        t_cfg.updated_at = now
    else:
        db.add(EditorialConfiguration(
            key="scoring_thresholds",
            value=DEFAULT_THRESHOLDS.copy(),
            description="Default canonical selection and tier thresholds",
            updated_at=now,
        ))

    await db.commit()
    return await get_scoring_config(db=db, _token=_token)
