import uuid
from datetime import datetime
from unittest.mock import create_autospec, AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.schemas.requests.reviews import ReviewRequest
from src.application.usecases.reviews import CreateReviewUseCase, FindReviewsUseCase, UpdateReviewUseCase, \
    DeleteReviewUseCase
from src.core.uow import SQLAlchemyUoW
from src.domain.books.entities import BookEntity
from src.domain.books.exceptions import BookNotExistException
from src.domain.books.protocols import BookRepositoryProtocol
from src.domain.reviews.entities import ReviewCreateEntity, ReviewEntity, ReviewUpdateEntity
from src.domain.reviews.exceptions import ReviewAlreadyExistException, ReviewNotExistException
from src.domain.reviews.mappers import ReviewSchemaMapper
from src.domain.reviews.protocols import ReviewRepositoryProtocol


@pytest.mark.asyncio
class TestCreateReviewUseCase:
    async def test_execute_success(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.create = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        book_id = uuid.uuid4()
        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        request = ReviewRequest(
            review="Test message",
            rating=5
        )

        entity = ReviewEntity(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            review=request.review,
            rating=request.rating,
            full_name="John Dul",
            book=book
        )

        create_entity = ReviewCreateEntity(
            review=request.review,
            rating=request.rating,
            book_id=book_id,
            user_id=user_id
        )

        response = object()

        book_repository.find_by_slug.return_value = book
        review_repository.create.return_value = entity
        mapper.from_entity_to_schema.return_value = response

        use_case = CreateReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper,
            uow=uow
        )

        result = await use_case.execute(
            slug=slug,
            user_id=user_id,
            data=request
        )

        assert result == response

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.create.assert_awaited_once_with(entity=create_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)

    async def test_execute_book_not_found(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.create = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        request = ReviewRequest(
            review="Test message",
            rating=5
        )

        book_repository.find_by_slug.return_value = None

        use_case = CreateReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(
                slug=slug,
                user_id=user_id,
                data=request
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.create.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()

    async def test_execute_review_already_exist(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.create = AsyncMock(side_effect=ReviewAlreadyExistException())
        mapper.from_entity_to_schema = Mock()

        book_id = uuid.uuid4()
        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        request = ReviewRequest(
            review="Test message",
            rating=5
        )

        create_entity = ReviewCreateEntity(
            review=request.review,
            rating=request.rating,
            book_id=book_id,
            user_id=user_id
        )

        book_repository.find_by_slug.return_value = book

        use_case = CreateReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper,
            uow=uow
        )

        with pytest.raises(ReviewAlreadyExistException):
            await use_case.execute(
                slug=slug,
                user_id=user_id,
                data=request
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.create.assert_awaited_once_with(entity=create_entity)
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestFindReviewsUseCase:
    async def test_execute_success(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)

        book_repository.find_by_slug = AsyncMock()
        review_repository.find_all_by_book_id = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        book_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        entities = [object(), object()]

        book_repository.find_by_slug.return_value = book
        review_repository.find_all_by_book_id.return_value = entities
        mapper.from_entity_to_schema.side_effect = [object(), object()]

        use_case = FindReviewsUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper
        )

        results = await use_case.execute(slug=slug)

        assert len(results) == 2
        assert mapper.from_entity_to_schema.call_count == 2

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.find_all_by_book_id.assert_awaited_once_with(book_id=book.id)

        for entity in entities:
            mapper.from_entity_to_schema.assert_any_call(entity=entity)

    async def test_execute_returns_empty_if_book_not_found(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)

        book_repository.find_by_slug = AsyncMock()
        review_repository.find_all_by_book_id = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        slug = "thomas-shelby"

        book_repository.find_by_slug.return_value = None

        use_case = FindReviewsUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper
        )

        results = await use_case.execute(slug=slug)
        assert results == []

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.find_all_by_book_id.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestUpdateReviewUseCase:
    async def test_execute_success(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.update = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        book_id = uuid.uuid4()
        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        request = ReviewRequest(
            review="Test message",
            rating=5
        )

        update_entity = ReviewUpdateEntity(
            review=request.review,
            rating=request.rating,
            book_id=book_id,
            user_id=user_id
        )

        entity = ReviewEntity(
            id=uuid.uuid4(),
            created_at=datetime.now(),
            review=request.review,
            rating=request.rating,
            full_name="John Dul",
            book=book
        )

        response = object()

        book_repository.find_by_slug.return_value = book
        review_repository.update.return_value = entity
        mapper.from_entity_to_schema.return_value = response

        use_case = UpdateReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper,
            uow=uow
        )

        result = await use_case.execute(
            slug=slug,
            user_id=user_id,
            data=request
        )

        assert result == response

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.update.assert_awaited_once_with(entity=update_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=entity)

    async def test_execute_book_not_found(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.update = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        request = ReviewRequest(
            review="Test message",
            rating=5
        )

        book_repository.find_by_slug.return_value = None

        use_case = UpdateReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(
                slug=slug,
                user_id=user_id,
                data=request
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.update.assert_not_awaited()
        mapper.from_entity_to_schema.assert_not_called()

    async def test_execute_review_not_exist(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        mapper = create_autospec(ReviewSchemaMapper, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.update = AsyncMock()
        mapper.from_entity_to_schema = Mock()

        book_id = uuid.uuid4()
        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        request = ReviewRequest(
            review="Test message",
            rating=5
        )

        update_entity = ReviewUpdateEntity(
            review=request.review,
            rating=request.rating,
            book_id=book_id,
            user_id=user_id
        )

        book_repository.find_by_slug.return_value = book
        review_repository.update.return_value = None

        use_case = UpdateReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            mapper=mapper,
            uow=uow
        )

        with pytest.raises(ReviewNotExistException):
            await use_case.execute(
                slug=slug,
                user_id=user_id,
                data=request
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.update.assert_awaited_once_with(entity=update_entity)
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestDeleteReviewUseCase:
    async def test_execute_success(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.delete_by_id = AsyncMock()

        book_id = uuid.uuid4()
        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        book_repository.find_by_slug.return_value = book
        review_repository.delete_by_id.return_value = True

        use_case = DeleteReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            uow=uow
        )

        await use_case.execute(
            user_id=user_id,
            slug=slug
        )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.delete_by_id.assert_awaited_once_with(
            user_id=user_id,
            book_id=book.id
        )

    async def test_execute_book_not_found(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.delete_by_id = AsyncMock()

        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book_repository.find_by_slug.return_value = None

        use_case = DeleteReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            uow=uow
        )

        with pytest.raises(BookNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.delete_by_id.assert_not_awaited()

    async def test_execute_review_not_found(self):
        review_repository = create_autospec(ReviewRepositoryProtocol, instance=True)
        book_repository = create_autospec(BookRepositoryProtocol, instance=True)
        fake_session = create_autospec(AsyncSession, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        book_repository.find_by_slug = AsyncMock()
        review_repository.delete_by_id = AsyncMock()

        book_id = uuid.uuid4()
        user_id = uuid.uuid4()
        slug = "thomas-shelby"

        book = create_autospec(BookEntity, instance=True)
        book.id = book_id

        book_repository.find_by_slug.return_value = book
        review_repository.delete_by_id.return_value = False

        use_case = DeleteReviewUseCase(
            book_repository=book_repository,
            review_repository=review_repository,
            uow=uow
        )

        with pytest.raises(ReviewNotExistException):
            await use_case.execute(
                user_id=user_id,
                slug=slug
            )

        book_repository.find_by_slug.assert_awaited_once_with(slug=slug)
        review_repository.delete_by_id.assert_awaited_once_with(
            user_id=user_id,
            book_id=book.id
        )