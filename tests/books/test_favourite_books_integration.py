import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uow import SQLAlchemyUoW
from src.domain.books.entities import BookCreateEntity, BookEntity
from src.domain.books.enums import Genre, BookReadingStatus
from src.domain.books.exceptions import FavouriteBookRepositoryException
from src.domain.user.entities import UserEntity, UserCreateEntity
from src.domain.user.enums import UserRole
from src.infrastructure.database.books.mappers import BookModelMapper, FavouriteBookModelMapper
from src.infrastructure.database.books.repositories import BookRepository, FavouriteBookRepository
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
class TestFavouriteBookRepository:
    async def test_add_success(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.add(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result.id is not None
            assert result.book == book_entity

    async def test_add_already_exist(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.add(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result is not None

        with pytest.raises(FavouriteBookRepositoryException):
            async with uow:
                await repository.add(
                    user_id=user_entity.id,
                    book_id=book_entity.id
                )

    async def test_delete_returns_true(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.add(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result is not None

        async with uow:
            result = await repository.delete(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result

    async def test_delete_returns_false(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.delete(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert not result

    async def test_find_all_returns_values(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.add(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result is not None

        results = await repository.find_all(user_id=user_entity.id)
        assert results == [result]

    async def test_find_all_returns_empty(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )

        results = await repository.find_all(user_id=user_entity.id)
        assert results == []

    async def test_update_status_success(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.add(
                user_id=user_entity.id,
                book_id=book_entity.id
            )

            assert result is not None

        async with uow:
            result = await repository.update_status(
                user_id=user_entity.id,
                book_id=book_entity.id,
                status=BookReadingStatus.READING
            )

            assert result.status == BookReadingStatus.READING

    async def test_update_status_returns_none(
            self,
            session: AsyncSession,
            user_entity: UserEntity,
            book_entity: BookEntity
    ):
        mapper = FavouriteBookModelMapper(mapper=BookModelMapper())
        repository = FavouriteBookRepository(
            mapper=mapper,
            session=session
        )
        uow = SQLAlchemyUoW(session)

        async with uow:
            result = await repository.update_status(
                user_id=user_entity.id,
                book_id=book_entity.id,
                status=BookReadingStatus.READING
            )

            assert result is None