from typing import AsyncGenerator, Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from starlette import status

from src.main import create_app
from src.core.database.database import Base, get_session

import fakeredis.aioredis


@pytest.fixture(scope="session")
def database_url(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("data")
    db_path = (db_dir / "test.db").as_posix()
    return f"sqlite+aiosqlite:///{db_path}"


@pytest.fixture(scope="session")
async def engine(database_url):
    engine = create_async_engine(database_url, echo=False, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_redis():
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    await redis.flushdb()
    yield redis
    await redis.aclose()


@pytest.fixture(scope="session", autouse=True)
async def create_test_schema(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, Any]:
    connection = await engine.connect()
    transaction = await connection.begin()
    nested = await connection.begin_nested()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    try:
        yield session
        await session.flush()
    except Exception:
        await nested.rollback()
        raise
    finally:
        await session.close()
        await nested.rollback()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
def app(session: AsyncSession, test_redis: fakeredis.FakeRedis):
    _app: FastAPI = create_app()

    async def _override_session():
        yield session

    async def _override_redis():
        yield test_redis

    _app.dependency_overrides[get_session] = _override_session
    return _app


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as async_client:
        yield async_client


@pytest.fixture
async def user_client(client):
    register_body = {
        "email": "test@mail.ru",
        "password": "test123@mail.ru",
        "is_admin": False
    }

    response = await client.post(
        url="/v1/auth/register",
        json=register_body
    )

    assert response.status_code == status.HTTP_201_CREATED

    login_body = {
        "email": "test@mail.ru",
        "password": "test123@mail.ru"
    }

    response = await client.post(
        url="/v1/auth/login",
        json=login_body
    )

    assert response.status_code == status.HTTP_200_OK

    token = response.json()["access_token"]
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client


@pytest.fixture
async def admin_client(client):
    register_body = {
        "email": "test@mail.ru",
        "password": "test123@mail.ru",
        "is_admin": True
    }

    response = await client.post(
        url="/v1/auth/register",
        json=register_body
    )

    assert response.status_code == status.HTTP_201_CREATED

    login_body = {
        "email": "test@mail.ru",
        "password": "test123@mail.ru"
    }

    response = await client.post(
        url="/v1/auth/login",
        json=login_body
    )

    assert response.status_code == status.HTTP_200_OK

    token = response.json()["access_token"]
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client