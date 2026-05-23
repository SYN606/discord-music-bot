import logging
from database.base import engine, Base
from config import settings

log = logging.getLogger("imposter.db")


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("✓ Database initialized")

    except Exception as e:
        log.error(f"DB Init Failed → {e}")
        if settings.is_dev():
            import traceback
            traceback.print_exc()