from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, and_, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.reviews.entities import ReviewCreateEntity, ReviewEntity, ReviewUpdateEntity
from src.domain.reviews.exceptions import ReviewAlreadyExistException, ReviewRepositoryException
from src.domain.reviews.protocols import ReviewRepositoryProtocol
from src.infrastructure.database.reviews.mappers import ReviewModelMapper
from src.infrastructure.database.reviews.models import ReviewModel


class ReviewRepository(ReviewRepositoryProtocol):
    def __init__(
            self,
            mapper: ReviewModelMapper,
            session: AsyncSession
    ):
        self.session = session
        self.mapper = mapper
        self.model = ReviewModel

    async def create(self, entity: ReviewCreateEntity) -> ReviewEntity:
        model = self.model(
            review=entity.review,
            rating=entity.rating,
            user_id=entity.user_id,
            book_id=entity.book_id
        )

        self.session.add(model)

        try:
            async with self.session.begin_nested():
                await self.session.flush()
        except IntegrityError as e:
            if "uq_user_book_review" in str(e):
                raise ReviewAlreadyExistException()
            raise ReviewRepositoryException()

        statement = (
            select(self.model)
            .options(
                selectinload(self.model.user),
                selectinload(self.model.book)
            )
            .where(self.model.id == model.id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None or model.book is None or model.user is None:
            raise ReviewRepositoryException()

        return self.mapper.from_model_to_entity(model=model)

    async def find_all_by_book_id(self, book_id: UUID) -> List[ReviewEntity]:
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.user),
                selectinload(self.model.book)
            )
            .where(self.model.book_id == book_id)
        )

        result = await self.session.execute(statement)
        models = list(result.scalars().all())

        return [
            self.mapper.from_model_to_entity(model=model)
            for model in models
        ]

    async def update(self, entity: ReviewUpdateEntity) -> Optional[ReviewEntity]:
        statement = (
            update(self.model)
            .values(
                review=entity.review,
                rating=entity.rating
            )
            .where(
                and_(
                    self.model.book_id == entity.book_id,
                    self.model.user_id == entity.user_id
                )
            )
            .returning(self.model.id)
        )

        result = await self.session.execute(statement)
        review_id = result.scalar_one_or_none()

        if review_id is None:
            return None

        statement = (
            select(self.model)
            .options(
                selectinload(self.model.user),
                selectinload(self.model.book)
            )
            .where(self.model.id == review_id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        return self.mapper.from_model_to_entity(model=model)

    async def delete_by_id(self, user_id: UUID, book_id: UUID) -> bool:
        statement = (
            delete(self.model)
            .where(
                and_(
                    self.model.book_id == book_id,
                    self.model.user_id == user_id
                )
            )
        )

        result = await self.session.execute(statement)
        return result.rowcount > 0
