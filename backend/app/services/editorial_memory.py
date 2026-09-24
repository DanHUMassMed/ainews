import re
from datetime import datetime, timezone, timedelta, date
from typing import Dict, Any, List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.edition import Edition
from backend.app.models.story import Story
from backend.app.models.memory import EditorialMemory
from backend.app.services.scoring import ScoringEngine
from backend.app.services.feedback import FeedbackService
from backend.app.schemas.editorial import (
    EditorialContextResponse,
    RecentStoryContextItem,
    EntityFrequencyItem,
    ScoringWeightsConfig,
    ScoringThresholdsConfig,
)

COMMON_ENTITIES = [
    "OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "NVIDIA", "Apple",
    "DeepSeek", "Mistral", "Cohere", "Amazon", "AMD", "Intel", "Hugging Face",
    "xAI", "Cerebras", "Groq", "TSMC", "Alibaba", "Tencent", "Baidu"
]

class EditorialMemoryService:
    @staticmethod
    def extract_entities(text: str) -> Set[str]:
        found = set()
        for ent in COMMON_ENTITIES:
            if re.search(r'\b' + re.escape(ent) + r'\b', text, re.IGNORECASE):
                found.add(ent)
        return found

    @classmethod
    async def get_editorial_context(cls, session: AsyncSession, days_lookback: int = 28) -> EditorialContextResponse:
        cutoff = date.today() - timedelta(days=days_lookback)
        
        # Query recent published editions and stories
        stmt = (
            select(Story)
            .join(Edition, Edition.id == Story.edition_id)
            .where(Edition.date >= cutoff, Edition.status == "published")
            .options(selectinload(Story.edition), selectinload(Story.categories), selectinload(Story.sources))
            .order_by(Edition.date.desc(), Story.position.asc())
        )
        res = await session.execute(stmt)
        stories = res.scalars().all()

        recent_story_items = []
        entity_counts: Dict[str, int] = {}

        for s in stories:
            source_url = s.sources[0].url if s.sources else None
            recent_story_items.append(
                RecentStoryContextItem(
                    title=s.title,
                    slug=s.slug,
                    date=s.edition.date,
                    categories=[c.name for c in s.categories],
                    why_it_matters=s.why_it_matters,
                    primary_source=source_url,
                )
            )
            # Count covered entities
            full_content = f"{s.title} {s.summary} {s.why_it_matters}"
            ents = cls.extract_entities(full_content)
            for e in ents:
                entity_counts[e] = entity_counts.get(e, 0) + 1

        entity_items = []
        repetition_avoid = []
        for ent, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True):
            warning = count >= 4  # flagged if repeated 4+ times in lookback
            if warning:
                repetition_avoid.append(f"{ent} (covered {count} times recently)")
            entity_items.append(
                EntityFrequencyItem(
                    entity=ent,
                    frequency_count=count,
                    repetition_warning=warning,
                )
            )

        cold_start = await FeedbackService.is_cold_start_active(session)
        weights_dict = await ScoringEngine.get_active_weights(session, cold_start_active=cold_start)
        weights_config = ScoringWeightsConfig(**weights_dict)
        thresholds_dict = await ScoringEngine.get_active_thresholds(session)
        thresholds_config = ScoringThresholdsConfig(**thresholds_dict)
        feedback_analytics = await FeedbackService.get_analytics(session, window_days=days_lookback)

        return EditorialContextResponse(
            publication_date=date.today(),
            lookback_days=days_lookback,
            recent_stories=recent_story_items,
            recent_covered_entities=entity_items,
            scoring_weights=weights_config,
            scoring_thresholds=thresholds_config,
            feedback_analytics=feedback_analytics,
            repetition_avoid_topics=repetition_avoid,
            portfolio_targets={"core": 70, "exploratory": 20, "contrarian": 10},
        )
