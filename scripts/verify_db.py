import asyncio
from sqlalchemy import text
from backend.app.core.database import AsyncSessionLocal

async def verify():
    async with AsyncSessionLocal() as session:
        print("--- Table Verification ---")
        tables_res = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """))
        tables = [row[0] for row in tables_res.fetchall()]
        print(f"Total tables: {len(tables)}")
        for t in tables:
            count_res = await session.execute(text(f"SELECT count(*) FROM {t};"))
            count = count_res.scalar()
            print(f"  • {t}: {count} rows")

        print("\n--- Index Verification ---")
        idx_res = await session.execute(text("""
            SELECT tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            ORDER BY tablename, indexname;
        """))
        indexes = idx_res.fetchall()
        print(f"Total indexes: {len(indexes)}")
        for tablename, indexname in indexes:
            print(f"  • [{tablename}] {indexname}")

        print("\n--- Full-Text Search Verification ---")
        fts_res = await session.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE indexname = 'ix_stories_fts';
        """))
        fts_index = fts_res.fetchone()
        if fts_index:
            print(f"  ✓ Full-text search index active: {fts_index[0]}")
            print(f"    Definition: {fts_index[1]}")
        else:
            print("  ✗ Warning: ix_stories_fts not found!")

if __name__ == "__main__":
    asyncio.run(verify())
