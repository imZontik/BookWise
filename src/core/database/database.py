from fastapi.params import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing_extensions import AsyncGenerator

from src.core.config import settings
from src.core.observability.database import setup_db_timing
from src.core.uow import SQLAlchemyUoW

engine = create_async_engine(str(settings.LOCAL_DATABASE_URL or settings.DATABASE_URL))
async_session = async_sessionmaker(engine, expire_on_commit=False)
setup_db_timing(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_session)) -> SQLAlchemyUoW:
    return SQLAlchemyUoW(session)


Base = declarative_base()