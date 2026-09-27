import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.category import Category
from backend.app.models.configuration import EditorialConfiguration

INITIAL_CATEGORIES = [
    {"name": "AI Models", "slug": "ai-models"},
    {"name": "Open Source", "slug": "open-source"},
    {"name": "Research", "slug": "research"},
    {"name": "Agents", "slug": "agents"},
    {"name": "Infrastructure", "slug": "infrastructure"},
    {"name": "Hardware", "slug": "hardware"},
    {"name": "Developer Tools", "slug": "developer-tools"},
    {"name": "Enterprise AI", "slug": "enterprise-ai"},
    {"name": "Robotics", "slug": "robotics"},
    {"name": "Regulation", "slug": "regulation"},
    {"name": "AI Business", "slug": "ai-business"},
    {"name": "Science & AI", "slug": "science-ai"},
]

INITIAL_CONFIGURATIONS = [
    {
        "key": "scoring_weights",
        "value": {
            "significance_weight": 0.35,
            "novelty_weight": 0.25,
            "evidence_weight": 0.20,
            "saturation_weight": 0.20,
            "feedback_weight": 0.15,
        },
        "description": "Weights for candidate composite scoring calculation",
    },
    {
        "key": "cold_start",
        "value": {
            "min_feedback_votes": 100,
            "cold_start_days": 30,
            "feedback_active": False,
        },
        "description": "Cold start threshold before reader feedback bias activates",
    },
    {
        "key": "portfolio_targets",
        "value": {
            "core_percent": 70,
            "exploratory_percent": 20,
            "contrarian_percent": 10,
        },
        "description": "Target portfolio distribution to prevent echo chambers",
    },
    {
        "key": "edition_constraints",
        "value": {
            "min_stories": 5,
            "target_stories": 8,
            "max_stories": 10,
            "discovery_window_hours": 28,
            "min_significance_threshold": 4.5,
        },
        "description": "Daily briefing structural story constraints and thresholds",
    },
    {
        "key": "schedule",
        "value": {
            "cron_expression": "0 5 * * *",
            "publication_time": "06:00 UTC",
        },
        "description": "Automated daily workflow schedule",
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Check and migrate legacy open-ai category if present
        res_legacy = await session.execute(select(Category).where(Category.slug == "open-ai"))
        legacy_cat = res_legacy.scalar_one_or_none()
        if legacy_cat:
            legacy_cat.name = "Open Source"
            legacy_cat.slug = "open-source"
            print("  ~ Migrated legacy category: 'open-ai' -> 'open-source'")

        print("Seeding categories...")
        for cat_data in INITIAL_CATEGORIES:
            res = await session.execute(select(Category).where(Category.slug == cat_data["slug"]))
            existing = res.scalar_one_or_none()
            if not existing:
                category = Category(name=cat_data["name"], slug=cat_data["slug"])
                session.add(category)
                print(f"  + Added category: {cat_data['name']} ({cat_data['slug']})")
            else:
                print(f"  . Exists: {cat_data['name']}")

        print("Seeding editorial configurations...")
        for cfg_data in INITIAL_CONFIGURATIONS:
            res = await session.execute(select(EditorialConfiguration).where(EditorialConfiguration.key == cfg_data["key"]))
            existing = res.scalar_one_or_none()
            if not existing:
                config = EditorialConfiguration(
                    key=cfg_data["key"],
                    value=cfg_data["value"],
                    description=cfg_data["description"],
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(config)
                print(f"  + Added config: {cfg_data['key']}")
            else:
                print(f"  . Exists: {cfg_data['key']}")

        await session.commit()
        print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
