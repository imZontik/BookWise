import uuid
from unittest.mock import create_autospec, AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.usecases.books import AddFavouriteBookUseCase, DeleteFavouriteBookUseCase, \
    FindFavouriteBooksUseCase, UpdateFavouriteBookStatusUseCase
from src.core.uow import SQLAlchemyUoW
from src.domain.books.entities import BookEntity, FavouriteBookEntity
from src.domain.books.enums import BookReadingStatus
from src.domain.books.exceptions import BookNotExistException, FavouriteBookAlreadyExistException, \
    FavouriteBookNotExistException
from src.domain.books.mappers import FavouriteBookSchemaMapper
from src.domain.books.protocols import BookRepositoryProtocol, FavouriteBookRepositoryProtocol


@pytest.mark.asyncio
class TestAddFavouriteBookUseCase:
    async def test_execute_success(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.add = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()
        book_id = uuid.uuid4()

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        entity = FavouriteBookEntity(
            id=uuid.uuid4(),
            status=BookReadingStatus.NOT_STARTED,
            book=book
        )

        response = object()

        book_repository.find_by_slug.return_value = book
        favourite_book_repository.add.return_value = entity
        mapper.from_entity_to_schema.return_value = response

        use_case = AddFavouriteBookUseCase(
            mapper=mapper,
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        result = await use_case.execute(
            user_id=user_id,
            slug=slug
        )

        assert result == response

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.add.assert_awaited_once_with(
            user_id=user_id,
            book_id=book_id
        )
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)

    async def test_execute_book_not_found(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.add = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()

        book_repository.find_by_slug.return_value = None

        use_case = AddFavouriteBookUseCase(
            mapper=mapper,
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.add.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()

    async def test_execute_favourite_book_already_exist(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.add = AsyncMock(side_effect=FavouriteBookAlreadyExistException())
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()
        book_id = uuid.uuid4()

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        book_repository.find_by_slug.return_value = book

        use_case = AddFavouriteBookUseCase(
            mapper=mapper,
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        with pytest.raises(FavouriteBookAlreadyExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.add.assert_awaited_once_with(
            user_id=user_id,
            book_id=book_id
        )
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestDeleteFavouriteBookUseCase:
    async def test_execute_success(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.delete = AsyncMock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()
        book_id = uuid.uuid4()

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        book_repository.find_by_slug.return_value = book
        favourite_book_repository.delete.return_value = True

        use_case = DeleteFavouriteBookUseCase(
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        await use_case.execute(
            user_id=user_id,
            slug=slug
        )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.delete.assert_awaited_once_with(
            user_id=user_id,
            book_id=book_id
        )

    async def test_execute_book_not_found(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.delete = AsyncMock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()

        book_repository.find_by_slug.return_value = None

        use_case = DeleteFavouriteBookUseCase(
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.delete.assert_not_awaited()

    async def test_execute_favourite_book_not_found(self):
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.delete = AsyncMock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()
        book_id = uuid.uuid4()

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        book_repository.find_by_slug.return_value = book
        favourite_book_repository.delete.return_value = False

        use_case = DeleteFavouriteBookUseCase(
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        with pytest.raises(FavouriteBookNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.delete.assert_awaited_once_with(
            user_id=user_id,
            book_id=book_id
        )


@pytest.mark.asyncio
class TestFindFavouriteBooksUseCase:
    async def test_execute_success(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)

        repository.find_all = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        entities = [object(), object(), object()]

        repository.find_all.return_value = entities
        mapper.from_entity_to_schema.side_effect = [object(), object(), object()]

        use_case = FindFavouriteBooksUseCase(
            repository=repository,
            mapper=mapper
        )

        result = await use_case.execute(user_id=uuid.uuid4())
        assert len(result) == 3
        assert mapper.from_entity_to_schema.call_count == 3

        for entity in entities:
            mapper.from_entity_to_schema.assert_any_call(entity=entity)


@pytest.mark.asyncio
class TestUpdateFavouriteBookStatusUseCase:
    async def test_execute_success(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.update_status = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()
        book_id = uuid.uuid4()

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        entity = FavouriteBookEntity(
            id=uuid.uuid4(),
            status=BookReadingStatus.READING,
            book=book
        )

        response = object()

        book_repository.find_by_slug.return_value = book
        favourite_book_repository.update_status.return_value = entity
        mapper.from_entity_to_schema.return_value = response

        use_case = UpdateFavouriteBookStatusUseCase(
            mapper=mapper,
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        result = await use_case.execute(
            user_id=user_id,
            slug=slug,
            status=BookReadingStatus.READING
        )

        assert result == response

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.update_status.assert_awaited_once_with(
            user_id=user_id,
            book_id=book_id,
            status=BookReadingStatus.READING
        )
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)

    async def test_execute_book_not_found(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.update_status = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()

        book_repository.find_by_slug.return_value = None

        use_case = UpdateFavouriteBookStatusUseCase(
            mapper=mapper,
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug,
                status=BookReadingStatus.READING
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.update_status.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()

    async def test_execute_favourite_book_not_exist(self):
        mapper = create_autospec(FavouriteBookSchemaMapper, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        favourite_book_repository = create_autospec(FavouriteBookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        favourite_book_repository.update_status = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"
        user_id = uuid.uuid4()
        book_id = uuid.uuid4()

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        book_repository.find_by_slug.return_value = book
        favourite_book_repository.update_status.return_value = None

        use_case = UpdateFavouriteBookStatusUseCase(
            mapper=mapper,
            book_repository=book_repository,
            favourite_book_repository=favourite_book_repository,
            uow=uow
        )

        with pytest.raises(FavouriteBookNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug,
                status=BookReadingStatus.READING
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        favourite_book_repository.update_status.assert_awaited_once_with(
            user_id=user_id,
            book_id=book_id,
            status=BookReadingStatus.READING
        )
        mapper.from_entity_to_schema.assert_not_called()