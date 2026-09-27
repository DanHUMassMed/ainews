#!/usr/bin/env python3
"""
Database Sanitization and Taxonomy Reclassification Script
1. Purges 16 mock/test/future editions and 62 mock stories.
2. Purges non-AI off-topic stories.
3. Fixes false-positive category assignments (e.g. Hardware on legal/software).
4. Classifies orphan stories (0 categories).
"""

import asyncio
from datetime import date
from sqlalchemy import select, delete, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.category import Category, story_categories
from backend.app.models.story import Story
from backend.app.models.edition import Edition

# Specific non-AI story titles to remove
NON_AI_TITLES = [
    "How BMW Group detects cost anomalies across 14,000 cloud accounts",
    "Serverless Git metrics pipeline delivers near-real-time QuickSight analytics",
    "OpenAI and AARP launch ChatGPT workshops for 1,000 older adults",
    "Google and UN Launch Searchable Open Data Commons Platform",
    "Google and UN Launch Open Platform for Global Statistics Discovery",
]

# Stories that have false positive 'hardware' tags to be removed
HARDWARE_FALSE_POSITIVES_TITLES = [
    "AWS details agentic video Q&A architecture with LLM orchestration",
    "GPT-6 Sol and Luna offer separate capability and cost tiers",
    "GPT-6 Sol and GPT-6 Luna launch on Amazon Bedrock",
    "OpenAI Astra for Law Debuts Legal Workflow Platform With Data-Aware Confidentiality Controls",
    "Introducing Astra for Law",
    "OpenAI launches Astra for Law with firm-specific data integration and confidential-work controls",
    "Introducing Kimi K3 on Amazon Bedrock",
    "Cooley Leverages ChatGPT Work to Automate IPO Legal Document Analysis",
    "DeepMind Veteran Cites 700-Agent Breach as Evidence of AI Misalignment Risk",
    "SageMaker AI adds ordered instance preference lists for training and processing jobs",
]

# Stories that are orphans (0 categories) and their rightful categories
ORPHAN_CLASSIFICATIONS = {
    "Altman Proposes UN-Backed Compute Governance for Frontier AI": ["regulation"],
    "Private AI Compute adds encrypted server-side memory for personal AI context": ["infrastructure"],
    "Jun Kim, oMLX creator and maintainer, joins Hugging Face to support the MLX community": ["developer-tools"],
    "Hugging Face Releases Tokenizers v1 with Faster Rust-Based Encode-Decode Pipeline": ["developer-tools"],
    "Gemini 3.8 Live adds low-latency streaming and extended reasoning modes": ["ai-models"],
    "Introducing Gemini 3.8 Live and 3.8 Live Extended Thinking": ["ai-models"],
    "Google links scientific AI progress to real-world impact metrics": ["science-ai", "research"],
    "Google Details AI Pipelines for Scientific Discovery and Clinical Use": ["science-ai", "research"],
    "Google Releases Open-Access AI Economy ATLAS with Millions of Data Points": ["ai-business", "research"],
    "OpenAI Proposes Coordinated Global AI Safety Standards and Reporting Gates": ["regulation"],
}


async def sanitize():
    print("=" * 80)
    print(" STARTING DATABASE SANITIZATION & TAXONOMY RECLASSIFICATION")
    print("=" * 80)

    async with AsyncSessionLocal() as session:
        # Step 1: Identify and delete mock/test editions and stories
        all_editions = (await session.execute(select(Edition))).scalars().all()
        mock_editions = [e for e in all_editions if e.date > date.today() or "Test" in e.title or "Valid" in e.title]
        mock_edition_ids = [e.id for e in mock_editions]

        print(f"\n[1] Deleting {len(mock_editions)} mock/test/future editions:")
        for e in mock_editions:
            print(f"    - {e.date} | {e.title}")

        if mock_edition_ids:
            # Delete stories associated with mock editions
            del_stories_stmt = delete(Story).where(Story.edition_id.in_(mock_edition_ids))
            res_stories = await session.execute(del_stories_stmt)
            print(f"    ✓ Deleted {res_stories.rowcount} associated mock stories")

            # Delete mock editions
            del_editions_stmt = delete(Edition).where(Edition.id.in_(mock_edition_ids))
            res_editions = await session.execute(del_editions_stmt)
            print(f"    ✓ Deleted {res_editions.rowcount} mock editions")

        # Step 2: Delete Non-AI off-topic stories
        print(f"\n[2] Purging non-AI scope violations:")
        for title in NON_AI_TITLES:
            del_stmt = delete(Story).where(Story.title == title)
            res = await session.execute(del_stmt)
            if res.rowcount > 0:
                print(f"    ✓ Deleted non-AI story: '{title}'")
            else:
                print(f"    . Story not found (or already removed): '{title}'")

        # Step 3: Load categories lookup
        cats = (await session.execute(select(Category))).scalars().all()
        cat_map = {c.slug: c for c in cats}

        # Step 4: Fix False Positive Hardware assignments
        print(f"\n[3] Stripping false-positive 'hardware' category tags:")
        hw_cat = cat_map.get("hardware")
        if hw_cat:
            for title in HARDWARE_FALSE_POSITIVES_TITLES:
                stmt = select(Story).options(selectinload(Story.categories)).where(Story.title == title)
                story = (await session.execute(stmt)).scalar_one_or_none()
                if story and hw_cat in story.categories:
                    story.categories.remove(hw_cat)
                    print(f"    ✓ Removed 'hardware' from: '{title}'")

        # Step 5: Classify Orphan Stories
        print(f"\n[4] Classifying orphan stories into appropriate domains:")
        for title, cat_slugs in ORPHAN_CLASSIFICATIONS.items():
            stmt = select(Story).options(selectinload(Story.categories)).where(Story.title == title)
            story = (await session.execute(stmt)).scalar_one_or_none()
            if story:
                for slug in cat_slugs:
                    if slug in cat_map and cat_map[slug] not in story.categories:
                        story.categories.append(cat_map[slug])
                print(f"    ✓ Assigned {cat_slugs} to: '{title}'")

        # Commit all changes
        await session.commit()
        print("\n" + "=" * 80)
        print(" SANITIZATION & RECLASSIFICATION COMPLETED SUCCESSFULLY")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(sanitize())
