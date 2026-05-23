import logging
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from database.base import engine
from config import settings

log = logging.getLogger("DV-Music.db")
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session():
    async with SessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            log.error(f"DB Error → {e}")

            if settings.is_dev():
                import traceback
                traceback.print_exc()

        finally:
            await session.close()