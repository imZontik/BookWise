import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uow import SQLAlchemyUoW
from src.domain.books.entities import BookEntity, BookCreateEntity
from src.domain.books.enums import Genre
from src.domain.reviews.entities import ReviewCreateEntity, ReviewUpdateEntity
from src.domain.reviews.exceptions import ReviewRepositoryException
from src.domain.user.entities import UserEntity, UserCreateEntity
from src.domain.user.enums import UserRole
from src.infrastructure.database.books.mappers import BookModelMapper
from src.infrastructure.database.books.repositories import BookRepository
from src.infrastructure.database.reviews.mappers import ReviewModelMapper
from src.infrastructure.database.reviews.repositories import ReviewRepository
from src.infrastructure.database.user.mappers import UserModelMapper
from src.infrastructure.database.user.repositories import UserRepository


@pytest.fixture
async def book_entity(session: AsyncSession) -> BookEntity:
    mapper = BookModelMapper()
    repository = BookRepository(
        session=session,
        mapper=mapper
    )
    uow = SQLAlchemyUoW(session)

    entity = BookCreateEntity(
        title="Thomas Shelby",
        slug="thomas-shelby",
        language="Русский",
        genre=Genre.FANTASY
    )

    async with uow:
        result = await repository.create(entity=entity)
        assert result is not None

    return result


@pytest.fixture
async def user_entity(session: AsyncSession) -> UserEntity:
    mapper = UserModelMapper()
    repository = UserRepository(
        session=session,
        mapper=mapper
    )
    uow = SQLAlchemyUoW(session)

    entity = UserCreateEntity(
        email="test@mail.com",
        hashed_password="pswd",
        first_name="John",
        last_name="Doe",
        role=UserRole.USER
    )

    async with uow:
        result = await repository.create(entity=entity)
        assert result is not None

    return result


@pytest.mark.asyncio
class TestReviewRepository:
    async def test_create_and_find(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        create_entity = ReviewCreateEntity(
            review="Super good",
            rating=5,
            user_id=user_entity.id,
            book_id=book_entity.id
        )

        async with uow:
            result = await repository.create(entity=create_entity)

            assert result.id is not None
            assert result.book.id == book_entity.id
            assert result.full_name == f"{user_entity.first_name} {user_entity.last_name}"
            assert result.review == create_entity.review
            assert result.rating == create_entity.rating

        results = await repository.find_all_by_book_id(book_id=book_entity.id)
        assert results == [result]

    async def test_create_review_repository_exception(
            self,
            session: AsyncSession,
            user_entity: UserEntity
    ):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        create_entity = ReviewCreateEntity(
            review="Super good",
            rating=5,
            user_id=user_entity.id,
            book_id=uuid.uuid4()
        )

        with pytest.raises(ReviewRepositoryException):
            async with uow:
                await repository.create(entity=create_entity)

    async def test_find_by_book_id_returns_empty(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )

        result = await repository.find_all_by_book_id(book_id=book_entity.id)
        assert result == []

    async def test_delete_by_id_returns_true(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        create_entity = ReviewCreateEntity(
            review="Super good",
            rating=5,
            user_id=user_entity.id,
            book_id=book_entity.id
        )

        async with uow:
            result = await repository.create(entity=create_entity)
            assert result.id is not None

        async with uow:
            result = await repository.delete_by_id(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result

    async def test_delete_by_id_returns_false(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.delete_by_id(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert not result

    async def test_update_success(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        create_entity = ReviewCreateEntity(
            review="Super good",
            rating=5,
            user_id=user_entity.id,
            book_id=book_entity.id
        )

        update_entity = ReviewUpdateEntity(
            review="So so",
            rating=3,
            user_id=user_entity.id,
            book_id=book_entity.id
        )

        async with uow:
            result = await repository.create(entity=create_entity)
            assert result.id is not None

        async with uow:
            result = await repository.update(entity=update_entity)
            assert result.review == update_entity.review
            assert result.rating == update_entity.rating

    async def test_update_returns_none(self, session: AsyncSession):
        mapper = ReviewModelMapper(
            mapper=BookModelMapper()
        )
        repository = ReviewRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        update_entity = ReviewUpdateEntity(
            review="So so",
            rating=3,
            user_id=uuid.uuid4(),
            book_id=uuid.uuid4()
        )

        async with uow:
            result = await repository.update(entity=update_entity)
            assert result is None


