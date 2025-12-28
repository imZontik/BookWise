from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, delete, update, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.books.entities import BookCreateEntity, BookEntity, BookUpdateEntity, BookFilterEntity, \
    FavouriteBookEntity
from src.domain.books.enums import BookReadingStatus
from src.domain.books.exceptions import BookAlreadyExistException, FavouriteBookAlreadyExistException, \
    FavouriteBookRepositoryException
from src.domain.books.protocols import BookRepositoryProtocol, FavouriteBookRepositoryProtocol
from src.infrastructure.database.books.mappers import BookModelMapper, FavouriteBookModelMapper
from src.infrastructure.database.books.models import BookModel, FavouriteBookModel


class BookRepository(BookRepositoryProtocol):
    def __init__(
            self,
            session: AsyncSession,
            mapper: BookModelMapper
    ):
        self.session = session
        self.mapper = mapper
        self.model = BookModel

    async def create(self, entity: BookCreateEntity) -> BookEntity:
        model = self.model(
            title=entity.title,
            slug=entity.slug,
            language=entity.language,
            description=entity.description,
            short_description=entity.short_description,
            publish_year=entity.publish_year,
            page_count=entity.page_count,
            author_id=entity.author_id,
            genre=entity.genre
        )

        self.session.add(model)

        try:
            async with self.session.begin_nested():
                await self.session.flush()
        except IntegrityError:
            raise BookAlreadyExistException()

        return self.mapper.from_model_to_entity(model=model)

    async def find_by_id(self, book_id: UUID) -> Optional[BookEntity]:
        statement = (
            select(self.model)
            .where(self.model.id == book_id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.from_model_to_entity(model=model)

        return None

    async def find_by_slug(self, slug: str) -> Optional[BookEntity]:
        statement = (
            select(self.model)
            .where(self.model.slug == slug)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.from_model_to_entity(model=model)

        return None

    async def find_all(self, filters: BookFilterEntity) -> List[BookEntity]:
        statement = select(self.model)

        if filters.genre is not None:
            statement = statement.where(self.model.genre == filters.genre)

        if filters.limit is not None:
            statement = statement.limit(filters.limit)

        if filters.year_from is not None:
            statement = statement.where(self.model.publish_year >= filters.year_from)

        if filters.year_to is not None:
            statement = statement.where(self.model.publish_year <= filters.year_to)

        if filters.pages_from is not None:
            statement = statement.where(self.model.page_count >= filters.pages_from)

        if filters.pages_to is not None:
            statement = statement.where(self.model.page_count <= filters.pages_to)

        result = await self.session.execute(statement)
        models = list(result.scalars().all())

        return [
            self.mapper.from_model_to_entity(model=model)
            for model in models
        ]

    async def delete_by_id(self, model_id: UUID) -> bool:
        statement = (
            delete(self.model)
            .where(self.model.id == model_id)
        )

        result = await self.session.execute(statement)
        return result.rowcount > 0

    async def update(self, entity: BookUpdateEntity) -> Optional[BookEntity]:
        statement = (
            update(self.model)
            .values(
                language=entity.language,
                description=entity.description,
                short_description=entity.short_description,
                publish_year=entity.publish_year,
                page_count=entity.page_count,
                author_id=entity.author_id,
                genre=entity.genre
            )
            .where(self.model.id == entity.id)
            .returning(self.model)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.from_model_to_entity(model=model)

        return None


class FavouriteBookRepository(FavouriteBookRepositoryProtocol):
    def __init__(
            self,
            session: AsyncSession,
            mapper: FavouriteBookModelMapper
    ):
        self.session = session
        self.mapper = mapper
        self.model = FavouriteBookModel

    async def add(self, user_id: UUID, book_id: UUID) -> FavouriteBookEntity:
        model = self.model(
            user_id=user_id,
            book_id=book_id
        )

        self.session.add(model)

        try:
            async with self.session.begin_nested():
                await self.session.flush()
        except IntegrityError as e:
            if "uq_user_book_review" in str(e):
                raise FavouriteBookAlreadyExistException()
            raise FavouriteBookRepositoryException()

        statement = (
            select(self.model)
            .options(selectinload(self.model.book))
            .where(self.model.id == model.id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None or model.book is None:
            raise FavouriteBookRepositoryException()

        return self.mapper.from_model_to_entity(model=model)

    async def delete(self, user_id: UUID, book_id: UUID) -> bool:
        statement = (
            delete(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.book_id == book_id
                )
            )
        )

        result = await self.session.execute(statement)
        return result.rowcount > 0

    async def find_all(self, user_id: UUID) -> List[FavouriteBookEntity]:
        statement = (
            select(self.model)
            .options(selectinload(self.model.book))
            .where(self.model.user_id == user_id)
        )

        result = await self.session.execute(statement)
        models = list(result.scalars().all())

        return [
            self.mapper.from_model_to_entity(model=model)
            for model in models
        ]

    async def update_status(
            self,
            user_id: UUID,
            book_id: UUID,
            status: BookReadingStatus
    ) -> Optional[FavouriteBookEntity]:
        statement = (
            update(self.model)
            .values(status=status)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.book_id == book_id
                )
            )
            .returning(self.model.id)
        )

        result = await self.session.execute(statement)
        favourite_book_id = result.scalar_one_or_none()

        if favourite_book_id is None:
            return None

        statement = (
            select(self.model)
            .options(selectinload(self.model.book))
            .where(self.model.id == favourite_book_id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        return self.mapper.from_model_to_entity(model=model)

