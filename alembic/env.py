from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context

from sqlalchemy.ext.asyncio import create_async_engine

import asyncio

from src.core.database.database import Base

from src.infrastructure.database.user.models import UserModel
from src.infrastructure.database.author.models import AuthorModel
from src.infrastructure.database.books.models import BookModel, FavouriteBookModel
from src.infrastructure.database.reviews.models import ReviewModel

from src.core.config import settings

config = context.config
target_metadata = Base.metadata

database_url = str(settings.LOCAL_DATABASE_URL or settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connection = create_async_engine(database_url, poolclass=pool.NullPool, future=True)

    async with connection.connect() as conn:
        await conn.run_sync(run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
