import uuid
from unittest.mock import create_autospec, AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.schemas.requests.books import BooksQuery, BookCreateRequest, BookUpdateRequest
from src.adapters.schemas.responses.books import BookResponse
from src.application.usecases.books import GetBooksUseCase, FindBookBySlugUseCase, DeleteBookUseCase, CreateBookUseCase, \
    UpdateBookUseCase
from src.core.uow import SQLAlchemyUoW
from src.domain.author.exceptions import AuthorNotExistException
from src.domain.author.protocols import AuthorRepositoryProtocol
from src.domain.books.entities import BookFilterEntity, BookCreateEntity, BookUpdateEntity, BookEntity
from src.domain.books.enums import Genre
from src.domain.books.exceptions import BookNotExistException, BookAlreadyExistException
from src.domain.books.mappers import BookSchemaMapper
from src.domain.books.protocols import BookRepositoryProtocol
from src.domain.cache.protocols import CacheManagerProtocol


@pytest.mark.asyncio
class TestGetBooksUseCase:
    async def test_execute_success(self):
        repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)

        query = BooksQuery(
            genre=None,
            limit=None,
            year_from=None,
            year_to=None,
            pages_to=None,
            pages_from=None
        )

        filters_entity = BookFilterEntity(**query.model_dump())
        find_all_results = [object()]
        use_case_result = [
            BookResponse(
                id=uuid.uuid4(),
                title="Test",
                slug="test",
                genre=Genre.FANTASY,
                language="Русский",
                description=None,
                short_description=None,
                publish_year=None,
                page_count=None,
                author_id=None
            )
        ]

        repository.find_all.return_value = find_all_results
        mapper.from_entity_to_schema.return_value = use_case_result[0]

        use_case = GetBooksUseCase(
            repository=repository,
            mapper=mapper
        )

        result = await use_case.execute(filters=query)
        assert result == use_case_result

        repository.find_all.assert_awaited_once_with(filters=filters_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=find_all_results[0])


@pytest.mark.asyncio
class TestFindBookBySlugUseCase:
    async def test_execute_success(self):
        repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        slug = "thomas-shelby"

        entity = object()
        response = create_autospec(BookResponse, instance=True)
        response.model_dump.return_value = object()

        repository.find_by_slug.return_value = entity
        mapper.from_entity_to_schema.return_value = response
        cache_manager.get_json.return_value = None

        use_case = FindBookBySlugUseCase(
            repository=repository,
            mapper=mapper,
            cache=cache_manager
        )

        result = await use_case.execute(slug=slug)
        assert result == response

        repository.find_by_slug.assert_awaited_once_with(slug=slug)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)

    async def test_execute_book_not_found(self):
        repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        slug = "thomas-shelby"
        repository.find_by_slug.return_value = None
        cache_manager.get_json.return_value = None

        use_case = FindBookBySlugUseCase(
            repository=repository,
            mapper=mapper,
            cache=cache_manager
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(slug=slug)

        repository.find_by_slug.assert_awaited_once_with(slug=slug)
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestDeleteBookUseCase:
    async def test_execute_success(self):
        repository = create_autospec(BookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        repository.delete_by_id.return_value = True

        book_id = uuid.uuid4()
        use_case = DeleteBookUseCase(
            repository=repository,
            uow=uow
        )

        await use_case.execute(book_id=book_id)

        repository.delete_by_id.assert_awaited_once_with(model_id=book_id)

    async def test_execute_book_not_found(self):
        repository = create_autospec(BookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        repository.delete_by_id.return_value = False

        book_id = uuid.uuid4()
        use_case = DeleteBookUseCase(
            repository=repository,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(book_id=book_id)

        repository.delete_by_id.assert_awaited_once_with(model_id=book_id)


@pytest.mark.asyncio
class TestCreateBookUseCase:
    async def test_execute_success_without_author_id(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        slug = "big-life"
        request = BookCreateRequest(
            title="Big Life",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        create_entity = BookCreateEntity(
            title=request.title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        response = BookResponse(
            id=uuid.uuid4(),
            title=request.title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        entity = object()

        book_repository.create.return_value = entity
        mapper.from_entity_to_schema.return_value = response

        use_case = CreateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow
        )

        result = await use_case.execute(data=request)
        assert result == response

        book_repository.create.assert_awaited_once_with(entity=create_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)
        author_repository.find_by_id.assert_not_awaited()

    async def test_execute_success_with_author_id(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        slug = "big-life"
        author_id = uuid.uuid4()

        request = BookCreateRequest(
            title="Big Life",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=author_id
        )

        create_entity = BookCreateEntity(
            title=request.title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        response = BookResponse(
            id=uuid.uuid4(),
            title=request.title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        entity = object()

        book_repository.create.return_value = entity
        mapper.from_entity_to_schema.return_value = response
        author_repository.find_by_id.return_value = object()

        use_case = CreateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow
        )

        result = await use_case.execute(data=request)
        assert result == response

        book_repository.create.assert_awaited_once_with(entity=create_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)
        author_repository.find_by_id.assert_awaited_once_with(model_id=author_id)

    async def test_execute_author_not_found(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        author_id = uuid.uuid4()

        request = BookCreateRequest(
            title="Big Life",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=author_id
        )

        author_repository.find_by_id.return_value = None

        use_case = CreateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow
        )

        with pytest.raises(AuthorNotExistException):
            await use_case.execute(data=request)

        author_repository.find_by_id.assert_awaited_once_with(model_id=author_id)
        book_repository.create.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()

    async def test_execute_book_already_exist(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        book_repository.create = AsyncMock(side_effect=BookAlreadyExistException)

        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        slug = "big-life"
        author_id = uuid.uuid4()

        request = BookCreateRequest(
            title="Big Life",
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=author_id
        )

        create_entity = BookCreateEntity(
            title=request.title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        author_repository.find_by_id.return_value = object()

        use_case = CreateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow
        )

        with pytest.raises(BookAlreadyExistException):
            await use_case.execute(data=request)

        author_repository.find_by_id.assert_awaited_once_with(model_id=author_id)
        book_repository.create.assert_awaited_once_with(entity=create_entity)
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestUpdateBookUseCase:
    async def test_execute_success_without_author_id(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_id = uuid.uuid4()
        title = "Thomas Shelby"
        slug = "thomas-shelby"

        request = BookUpdateRequest(
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=None
        )

        update_entity = BookUpdateEntity(
            id=book_id,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        response = BookResponse(
            id=uuid.uuid4(),
            title=title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        entity = create_autospec(BookEntity, instance=True)
        entity.slug = "test"

        book_repository.update.return_value = entity
        mapper.from_entity_to_schema.return_value = response

        use_case = UpdateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow,
            cache=cache_manager
        )

        result = await use_case.execute(book_id=book_id, data=request)
        assert result == response

        book_repository.update.assert_awaited_once_with(entity=update_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)
        author_repository.find_by_id.assert_not_awaited()

    async def test_execute_success_with_author_id(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)
        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        book_id = uuid.uuid4()
        title = "Thomas Shelby"
        slug = "thomas-shelby"
        author_id = uuid.uuid4()

        request = BookUpdateRequest(
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=author_id
        )

        update_entity = BookUpdateEntity(
            id=book_id,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        response = BookResponse(
            id=uuid.uuid4(),
            title=title,
            slug=slug,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        entity = create_autospec(BookEntity, instance=True)
        entity.slug = "test"

        book_repository.update.return_value = entity
        mapper.from_entity_to_schema.return_value = response
        author_repository.find_by_id.return_value = object()

        use_case = UpdateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow,
            cache=cache_manager
        )

        result = await use_case.execute(book_id=book_id, data=request)
        assert result == response

        book_repository.update.assert_awaited_once_with(entity=update_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)
        author_repository.find_by_id.assert_awaited_once_with(model_id=author_id)

    async def test_execute_author_not_found(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)
        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        book_id = uuid.uuid4()
        author_id = uuid.uuid4()

        request = BookUpdateRequest(
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=author_id
        )

        author_repository.find_by_id.return_value = None

        use_case = UpdateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow,
            cache=cache_manager
        )

        with pytest.raises(AuthorNotExistException):
            await use_case.execute(book_id=book_id, data=request)

        author_repository.find_by_id.assert_awaited_once_with(model_id=author_id)
        book_repository.update.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()

    async def test_execute_book_not_found(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        author_repository = create_autospec(AuthorRepositoryProtocol, instance=True)
        mapper = create_autospec(BookSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)
        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        book_id = uuid.uuid4()
        author_id = uuid.uuid4()

        request = BookUpdateRequest(
            genre=Genre.FANTASY,
            language="Русский",
            description=None,
            short_description=None,
            publish_year=None,
            page_count=None,
            author_id=author_id
        )

        update_entity = BookUpdateEntity(
            id=book_id,
            genre=request.genre,
            language=request.language,
            description=request.description,
            short_description=request.short_description,
            publish_year=request.publish_year,
            page_count=request.page_count,
            author_id=request.author_id
        )

        author_repository.find_by_id.return_value = object()
        book_repository.update.return_value = None

        use_case = UpdateBookUseCase(
            book_repository=book_repository,
            author_repository=author_repository,
            mapper=mapper,
            uow=uow,
            cache=cache_manager
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(book_id=book_id, data=request)

        author_repository.find_by_id.assert_awaited_once_with(model_id=author_id)
        book_repository.update.assert_awaited_once_with(entity=update_entity)
        mapper.from_entity_to_schema.assert_not_called()