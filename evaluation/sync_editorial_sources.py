#!/usr/bin/env python3
"""Sync evaluated whitelist sources and scoping policies to Editorial Memory.

Stores the source evaluations, tier definitions, and scoping guidelines
into PostgreSQL `editorial_memories` for runtime enforcement by the
Discovery and Research agents.
"""

import os
import sys
import csv
import json
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import select

# Add project root to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.memory import EditorialMemory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ainews.sync_sources")

async def sync_evaluated_sources():
    evaluated_csv = os.path.join(os.path.dirname(__file__), "whitelist_evaluated.csv")
    if not os.path.exists(evaluated_csv):
        logger.error(f"File not found: {evaluated_csv}. Please run evaluate_whitelist.py first.")
        return

    with open(evaluated_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sources = list(reader)

    logger.info(f"Loaded {len(sources)} evaluated sources from {evaluated_csv}")

    payload = {
        "version": "1.0",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "total_sources": len(sources),
        "sources": sources,
        "scoping_rules": {
            "tier_1_direct_labs": "Ingest primary technical announcements via RSS feed or stealth markdown scraping.",
            "tier_2_paywalled_press": "Secondary discovery only. Ingest headlines via SearXNG; require primary source confirmation.",
            "tier_3_newsletters": "Ingest directly via clean RSS endpoints (/feed) for pristine content.",
            "tier_4_preprints": "Query ArXiv API with explicit categories; do not scrape raw HTML.",
            "tier_4_community": "Query Reddit JSON API with threshold score >= 100."
        }
    }

    async with AsyncSessionLocal() as session:
        # Check if record already exists
        stmt = select(EditorialMemory).where(
            EditorialMemory.memory_type == "source_whitelist",
            EditorialMemory.key == "source_domain_whitelist"
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.payload = payload
            existing.updated_at = datetime.now(timezone.utc)
            logger.info("Updated existing source_domain_whitelist memory entry.")
        else:
            new_mem = EditorialMemory(
                id=uuid.uuid4(),
                memory_type="source_whitelist",
                key="source_domain_whitelist",
                payload=payload,
            )
            session.add(new_mem)
            logger.info("Created new source_domain_whitelist memory entry.")

        await session.commit()
    logger.info("Successfully synced evaluated sources to editorial_memories database.")

if __name__ == "__main__":
    asyncio.run(sync_evaluated_sources())
