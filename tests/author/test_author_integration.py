from typing import Dict, Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uow import SQLAlchemyUoW
from src.domain.author.entities import AuthorCreateEntity
from src.domain.author.exceptions import AuthorAlreadyExistException
from src.infrastructure.database.author.mappers import AuthorModelMapper
from src.infrastructure.database.author.repositories import AuthorRepository


@pytest.mark.asyncio
class TestAuthorRepository:
    @pytest.mark.parametrize(
        "author_data",
        [
            {
                "name": "John Doe",
                "slug": "johh-doe",
                "bio": None,
                "birth_date": None,
                "death_date": None,
                "country": None
            },
            {
                "name": "John Doe",
                "slug": "johh-doe",
                "bio": "Good writer",
                "birth_date": None,
                "death_date": None,
                "country": None
            },
            {
                "name": "John Doe",
                "slug": "johh-doe",
                "bio": "Good writer",
                "birth_date": None,
                "death_date": None,
                "country": "Russia"
            }
        ]
    )
    async def test_create_and_find(
            self,
            session: AsyncSession,
            author_data: Dict[str, Any]
    ):
        mapper = AuthorModelMapper()
        repository = AuthorRepository(
            session=session,
            mapper=mapper
        )
        uow = SQLAlchemyUoW(session)
        entity = AuthorCreateEntity(**author_data)

        async with uow:
            result = await repository.create(entity=entity)

            assert result.id is not None
            assert result.name == entity.name
            assert result.slug == entity.slug
            assert result.country == entity.country

            result_by_id = await repository.find_by_id(model_id=result.id)
            assert result_by_id is not None
            assert result_by_id.id == result.id
            assert result_by_id.slug == result.slug

            result_by_slug = await repository.find_by_slug(slug=entity.slug)
            assert result_by_slug is not None
            assert result_by_slug.id == result.id

    @pytest.mark.asyncio
    async def test_create_author_already_exist(self, session: AsyncSession):
        mapper = AuthorModelMapper()
        repository = AuthorRepository(
            session=session,
            mapper=mapper
        )

        uow1 = SQLAlchemyUoW(session)
        uow2 = SQLAlchemyUoW(session)

        entity = AuthorCreateEntity(
            name="Anton Email",
            slug="anton-email",
            bio=None,
            death_date=None,
            birth_date=None,
            country=None
        )

        async with uow1:
            result = await repository.create(entity=entity)
            assert result.id is not None

        with pytest.raises(AuthorAlreadyExistException):
            async with uow2:
                await repository.create(entity=entity)

    @pytest.mark.asyncio
    async def test_delete_by_id(self, session: AsyncSession):
        mapper = AuthorModelMapper()
        repository = AuthorRepository(
            session=session,
            mapper=mapper
        )

        uow1 = SQLAlchemyUoW(session)
        uow2 = SQLAlchemyUoW(session)

        entity = AuthorCreateEntity(
            name="Anton Email",
            slug="anton-email",
            bio=None,
            death_date=None,
            birth_date=None,
            country=None
        )

        async with uow1:
            result = await repository.create(entity=entity)
            assert result.id is not None

        async with uow2:
            result = await repository.delete_by_id(model_id=result.id)
            assert result

    @pytest.mark.asyncio
    async def test_update_photo_url(self, session: AsyncSession):
        mapper = AuthorModelMapper()
        repository = AuthorRepository(
            session=session,
            mapper=mapper
        )

        uow = SQLAlchemyUoW(session)

        entity = AuthorCreateEntity(
            name="Anton Email",
            slug="anton-email",
            bio=None,
            death_date=None,
            birth_date=None,
            country=None
        )
        photo_url = "http://test.com"

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None

            updated_result = await repository.update_photo_url(
                model_id=result.id,
                photo_url=photo_url
            )
            assert updated_result.id == result.id
            assert updated_result.photo_url == photo_url