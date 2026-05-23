import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from config import settings

log = logging.getLogger("imposter.db")
DB_URL = "sqlite+aiosqlite:///./database/data.db"
engine = create_async_engine(DB_URL, echo=settings.is_dev(), future=True)
Base = declarative_base()
