"""In-process async job dispatcher (Redis/ARQ can replace this later)."""

from __future__ import annotations

import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


def enqueue_ingestion(source_id: uuid.UUID) -> None:
    """Fire-and-forget ingestion on the event loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    async def _run() -> None:
        from app.ingestion.pipelines.ingest import run_ingestion
        await run_ingestion(source_id)

    if loop and loop.is_running():
        loop.create_task(_run())
    else:
        asyncio.run(_run())
    logger.info("Enqueued ingestion for source %s", source_id)
