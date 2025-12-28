import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uow import SQLAlchemyUoW
from src.domain.books.entities import BookCreateEntity, BookUpdateEntity, BookFilterEntity
from src.domain.books.enums import Genre
from src.domain.books.exceptions import BookAlreadyExistException
from src.infrastructure.database.books.mappers import BookModelMapper
from src.infrastructure.database.books.repositories import BookRepository


@pytest.mark.asyncio
class TestBookRepository:
    async def test_create_and_find(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        entity = BookCreateEntity(
            title="Thomas Shelby",
            slug="thomas-shelby",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None
            assert result.title == entity.title
            assert result.slug == entity.slug
            assert result.genre == entity.genre

            result_by_id = await repository.find_by_id(book_id=result.id)
            assert result_by_id is not None
            assert result_by_id.id == result.id

            result_by_slug = await repository.find_by_slug(slug=entity.slug)
            assert result_by_slug is not None
            assert result_by_slug.id == result.id

    async def test_create_book_already_exist(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)

        entity = BookCreateEntity(
            title="Thomas Shelby",
            slug="thomas-shelby",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None

        with pytest.raises(BookAlreadyExistException):
            async with uow:
                await repository.create(entity=entity)

    async def test_find_by_id_returns_none(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        book_id = uuid.uuid4()
        result = await repository.find_by_id(book_id=book_id)
        assert result is None

    async def test_find_by_slug_returns_none(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        slug = "thomas-shelby"
        result = await repository.find_by_slug(slug=slug)
        assert result is None

    async def test_delete_by_id_returns_true(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)

        entity = BookCreateEntity(
            title="Thomas Shelby",
            slug="thomas-shelby",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None

        async with uow:
            result = await repository.delete_by_id(model_id=result.id)
            assert result

    async def test_delete_by_id_returns_false(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)
        book_id = uuid.uuid4()

        async with uow:
            result = await repository.delete_by_id(model_id=book_id)
            assert not result

    async def test_update_success(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)

        entity = BookCreateEntity(
            title="Thomas Shelby",
            slug="thomas-shelby",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None

        update_entity = BookUpdateEntity(
            id=result.id,
            genre=Genre.FANTASY,
            language="English",
            description=None,
            short_description=None,
            publish_year=2020,
            page_count=None,
            author_id=None
        )

        async with uow:
            updated_result = await repository.update(entity=update_entity)
            assert updated_result.id == result.id
            assert updated_result.title == result.title
            assert updated_result.publish_year == update_entity.publish_year
            assert updated_result.language == update_entity.language

    async def test_update_returns_none(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)
        update_entity = BookUpdateEntity(
            id=uuid.uuid4(),
            genre=Genre.FANTASY,
            language="English",
            description=None,
            short_description=None,
            publish_year=2020,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.update(entity=update_entity)
            assert result is None

    async def test_find_all_returns_empty(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        results = await repository.find_all(filters=BookFilterEntity())
        assert results == list()

    async def test_find_all_without_filters(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)

        entity = BookCreateEntity(
            title="Thomas Shelby",
            slug="thomas-shelby",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        entity2 = BookCreateEntity(
            title="Cristiano Ronaldo",
            slug="cristiano-ronaldo",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None

            result = await repository.create(entity=entity2)
            assert result.id is not None

        results = await repository.find_all(filters=BookFilterEntity())
        assert len(results) == 2

    async def test_find_all_with_filters(self, session: AsyncSession):
        mapper = BookModelMapper()
        repository = BookRepository(
            mapper=mapper,
            session=session
        )

        uow = SQLAlchemyUoW(session)

        entity = BookCreateEntity(
            title="Thomas Shelby",
            slug="thomas-shelby",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=2017,
            page_count=None,
            author_id=None
        )

        entity2 = BookCreateEntity(
            title="Cristiano Ronaldo",
            slug="cristiano-ronaldo",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=2020,
            page_count=None,
            author_id=None
        )

        async with uow:
            result = await repository.create(entity=entity)
            assert result.id is not None

            result = await repository.create(entity=entity2)
            assert result.id is not None

        filters = BookFilterEntity(
            year_from=2018,
            genre=Genre.FANTASY
        )

        results = await repository.find_all(filters=filters)
        assert len(results) == 1
        assert results[0].title == entity2.title