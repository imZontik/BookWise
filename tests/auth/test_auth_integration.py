import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uow import SQLAlchemyUoW
from src.domain.user.entities import UserCreateEntity
from src.domain.user.enums import UserRole
from src.domain.user.exceptions import UserAlreadyExistException
from src.infrastructure.database.user.mappers import UserModelMapper
from src.infrastructure.database.user.repositories import UserRepository


@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_and_find(self, session: AsyncSession):
        mapper = UserModelMapper()
        repository = UserRepository(
            session=session,
            mapper=mapper
        )
        uow = SQLAlchemyUoW(session)

        entity = UserCreateEntity(
            email="user@email.com",
            hashed_password="hashed123",
            first_name="Nikita",
            last_name="Superman",
            role=UserRole.USER
        )

        async with uow:
            result = await repository.create(entity=entity)

            assert result.id is not None
            assert result.email == entity.email
            assert result.hashed_password == entity.hashed_password
            assert result.first_name == entity.first_name
            assert result.last_name == entity.last_name

            result_by_id = await repository.find_by_id(model_id=result.id)
            assert result_by_id.id == result.id
            assert result_by_id.email == entity.email

            result_by_email = await repository.find_by_email(email=entity.email)
            assert result_by_email.id == result.id
            assert result_by_email.email == entity.email

    async def test_find_by_email_returns_none(self, session: AsyncSession):
        mapper = UserModelMapper()
        repository = UserRepository(
            session=session,
            mapper=mapper
        )

        result = await repository.find_by_email(email="test@email.com")
        assert result is None

    async def test_find_by_id_returns_none(self, session: AsyncSession):
        mapper = UserModelMapper()
        repository = UserRepository(
            session=session,
            mapper=mapper
        )

        result = await repository.find_by_id(model_id=uuid.uuid4())
        assert result is None

    async def test_create_with_duplicate_email_raise_error(self, session: AsyncSession):
        mapper = UserModelMapper()
        repository = UserRepository(
            session=session,
            mapper=mapper
        )

        entity = UserCreateEntity(
            email="user@email.com",
            hashed_password="hashed123",
            first_name="Nikita",
            last_name="Superman",
            role=UserRole.USER
        )

        uow1 = SQLAlchemyUoW(session)
        uow2 = SQLAlchemyUoW(session)

        async with uow1:
            result = await repository.create(entity=entity)
            assert result is not None

        with pytest.raises(UserAlreadyExistException):
            async with uow2:
                await repository.create(entity=entity)