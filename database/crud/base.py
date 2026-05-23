import logging
import traceback
from typing import Type, TypeVar, Generic, Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeMeta

from database.session import SessionLocal
from config import settings

log = logging.getLogger("imposter.db")

T = TypeVar("T", bound=DeclarativeMeta)


class BaseCRUD(Generic[T]):
    model: Type[T]

    # INTERNAL EXECUTOR
    @classmethod
    async def _run(cls, fn):
        if not hasattr(cls, "model") or cls.model is None:
            raise RuntimeError(f"{cls.__name__} → model not defined")

        async with SessionLocal() as session:
            try:
                return await fn(session)

            except SQLAlchemyError as e:
                await session.rollback()
                log.error(f"{cls.__name__} DB → {e}")

                if settings.is_dev():
                    traceback.print_exc()

                return None

            except Exception as e:
                await session.rollback()
                log.error(f"{cls.__name__} ERR → {e}")

                if settings.is_dev():
                    traceback.print_exc()

                return None

    # READ
    @classmethod
    async def get(cls, **filters):
        async def run(session):
            result = await session.execute(
                select(cls.model).filter_by(**filters)
            )
            return result.scalar_one_or_none()

        return await cls._run(run)

    @classmethod
    async def get_all(cls, **filters):
        async def run(session):
            result = await session.execute(
                select(cls.model).filter_by(**filters)
            )
            return result.scalars().all()

        return await cls._run(run)

    # CREATE
    @classmethod
    async def create(cls, **data):
        async def run(session):
            obj = cls.model(**data) # type: ignore
            session.add(obj)
            await session.commit()
            return obj

        return await cls._run(run)

    # UPDATE
    @classmethod
    async def update(cls, filters: Dict[str, Any], data: Dict[str, Any]):
        async def run(session):
            result = await session.execute(
                select(cls.model).filter_by(**filters)
            )
            obj = result.scalar_one_or_none()

            if not obj:
                return None

            for k, v in data.items():
                setattr(obj, k, v)

            await session.commit()
            return obj

        return await cls._run(run)

    # DELETE
    @classmethod
    async def delete(cls, **filters):
        async def run(session):
            result = await session.execute(
                select(cls.model).filter_by(**filters)
            )
            obj = result.scalar_one_or_none()

            if not obj:
                return False

            await session.delete(obj)
            await session.commit()
            return True

        return await cls._run(run)

    # UPSERT
    @classmethod
    async def upsert(cls, filters: Dict[str, Any], data: Dict[str, Any]):
        async def run(session):
            result = await session.execute(
                select(cls.model).filter_by(**filters)
            )
            obj = result.scalar_one_or_none()

            if obj:
                for k, v in data.items():
                    setattr(obj, k, v)
            else:
                obj = cls.model(**filters, **data) # type: ignore
                session.add(obj)

            await session.commit()
            return obj

        return await cls._run(run)