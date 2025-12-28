from typing import List
from uuid import UUID

from src.adapters.schemas.requests.reviews import ReviewRequest
from src.adapters.schemas.responses.reviews import ReviewResponse
from src.core.uow import SQLAlchemyUoW
from src.domain.books.exceptions import BookNotExistException
from src.domain.books.protocols import BookRepositoryProtocol
from src.domain.reviews.entities import ReviewCreateEntity, ReviewUpdateEntity
from src.domain.reviews.exceptions import ReviewNotExistException
from src.domain.reviews.mappers import ReviewSchemaMapper
from src.domain.reviews.protocols import CreateReviewUseCaseProtocol, ReviewRepositoryProtocol, \
    FindReviewsUseCaseProtocol, UpdateReviewUseCaseProtocol, DeleteReviewUseCaseProtocol


class CreateReviewUseCase(CreateReviewUseCaseProtocol):
    def __init__(
            self,
            review_repository: ReviewRepositoryProtocol,
            book_repository: BookRepositoryProtocol,
            mapper: ReviewSchemaMapper,
            uow: SQLAlchemyUoW
    ):
        self.review_repository = review_repository
        self.book_repository = book_repository
        self.mapper = mapper
        self.uow = uow

    async def execute(
            self,
            slug: str,
            user_id: UUID,
            data: ReviewRequest
    ) -> ReviewResponse:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            raise BookNotExistException()

        entity = ReviewCreateEntity(
            review=data.review,
            rating=data.rating,
            book_id=book.id,
            user_id=user_id
        )

        async with self.uow:
            result = await self.review_repository.create(entity=entity)
            return self.mapper.from_entity_to_schema(entity=result)


class FindReviewsUseCase(FindReviewsUseCaseProtocol):
    def __init__(
            self,
            review_repository: ReviewRepositoryProtocol,
            book_repository: BookRepositoryProtocol,
            mapper: ReviewSchemaMapper
    ):
        self.review_repository = review_repository
        self.book_repository = book_repository
        self.mapper = mapper

    async def execute(self, slug: str) -> List[ReviewResponse]:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            return []

        entities = await self.review_repository.find_all_by_book_id(book_id=book.id)
        return [
            self.mapper.from_entity_to_schema(entity=entity)
            for entity in entities
        ]


class UpdateReviewUseCase(UpdateReviewUseCaseProtocol):
    def __init__(
            self,
            review_repository: ReviewRepositoryProtocol,
            book_repository: BookRepositoryProtocol,
            mapper: ReviewSchemaMapper,
            uow: SQLAlchemyUoW
    ):
        self.review_repository = review_repository
        self.book_repository = book_repository
        self.mapper = mapper
        self.uow = uow

    async def execute(
            self,
            slug: str,
            user_id: UUID,
            data: ReviewRequest
    ) -> ReviewResponse:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            raise BookNotExistException()

        entity = ReviewUpdateEntity(
            review=data.review,
            rating=data.rating,
            book_id=book.id,
            user_id=user_id
        )

        async with self.uow:
            result = await self.review_repository.update(entity=entity)

            if result is None:
                raise ReviewNotExistException()

            return self.mapper.from_entity_to_schema(entity=result)


class DeleteReviewUseCase(DeleteReviewUseCaseProtocol):
    def __init__(
            self,
            review_repository: ReviewRepositoryProtocol,
            book_repository: BookRepositoryProtocol,
            uow: SQLAlchemyUoW
    ):
        self.review_repository = review_repository
        self.book_repository = book_repository
        self.uow = uow

    async def execute(self, user_id: UUID, slug: str) -> None:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            raise BookNotExistException()

        async with self.uow:
            result = await self.review_repository.delete_by_id(
                user_id=user_id,
                book_id=book.id
            )

            if not result:
                raise ReviewNotExistException()