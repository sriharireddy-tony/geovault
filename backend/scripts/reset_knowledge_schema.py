"""Drop outdated knowledge tables and recreate from current models.

Safe for local/dev: only knowledge-domain tables are reset.
Users, tenants, media, and projects are left intact.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.database import engine
from app.models import Base
import app.domains.knowledge.models  # noqa: F401


KNOWLEDGE_TABLES = [
    "message_citations",
    "conversation_sources",
    "messages",
    "conversations",
    "document_chunks",
    "content_blocks",
    "ingestion_jobs",
    "ai_usage_records",
    "knowledge_sources",
    "knowledge_space_members",
    "knowledge_spaces",
]


async def main() -> None:
    async with engine.begin() as conn:
        for table in KNOWLEDGE_TABLES:
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            print(f"dropped {table}")
        await conn.run_sync(Base.metadata.create_all)
        print("recreated tables from models")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
