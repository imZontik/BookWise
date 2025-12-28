from typing import Protocol, List, Optional
from uuid import UUID

from src.adapters.schemas.requests.reviews import ReviewRequest
from src.adapters.schemas.responses.reviews import ReviewResponse
from src.domain.reviews.entities import ReviewCreateEntity, ReviewEntity, ReviewUpdateEntity


class ReviewRepositoryProtocol(Protocol):
    async def create(self, entity: ReviewCreateEntity) -> ReviewEntity: ...
    async def find_all_by_book_id(self, book_id: UUID) -> List[ReviewEntity]: ...
    async def update(self, entity: ReviewUpdateEntity) -> Optional[ReviewEntity]: ...
    async def delete_by_id(self, user_id: UUID, book_id: UUID) -> bool: ...


class CreateReviewUseCaseProtocol(Protocol):
    async def execute(
            self,
            slug: str,
            user_id: UUID,
            data: ReviewRequest
    ) -> ReviewResponse: ...


class FindReviewsUseCaseProtocol(Protocol):
    async def execute(self, slug: str) -> List[ReviewResponse]: ...


class UpdateReviewUseCaseProtocol(Protocol):
    async def execute(
            self,
            slug: str,
            user_id: UUID,
            data: ReviewRequest
    ) -> ReviewResponse: ...


class DeleteReviewUseCaseProtocol(Protocol):
    async def execute(self, user_id: UUID, slug: str) -> None: ...