from typing import Protocol, Optional, List
from uuid import UUID

from src.adapters.schemas.requests.books import BookCreateRequest, BookUpdateRequest, BooksQuery
from src.adapters.schemas.responses.books import BookResponse, FavouriteBookResponse
from src.domain.books.entities import BookCreateEntity, BookEntity, BookUpdateEntity, BookFilterEntity, \
    FavouriteBookEntity
from src.domain.books.enums import BookReadingStatus


class BookRepositoryProtocol(Protocol):
    async def create(self, entity: BookCreateEntity) -> BookEntity: ...
    async def find_by_slug(self, slug: str) -> Optional[BookEntity]: ...
    async def find_by_id(self, book_id: UUID) -> Optional[BookEntity]: ...
    async def find_all(self, filters: BookFilterEntity) -> List[BookEntity]: ...
    async def delete_by_id(self, model_id: UUID) -> bool: ...
    async def update(self, entity: BookUpdateEntity) -> Optional[BookEntity]: ...


class FavouriteBookRepositoryProtocol(Protocol):
    async def add(self, user_id: UUID, book_id: UUID) -> FavouriteBookEntity: ...
    async def delete(self, user_id: UUID, book_id: UUID) -> bool: ...
    async def find_all(self, user_id: UUID) -> List[FavouriteBookEntity]: ...
    async def update_status(
            self,
            user_id: UUID,
            book_id: UUID,
            status: BookReadingStatus
    ) -> Optional[FavouriteBookEntity]: ...


class CreateBookUseCaseProtocol(Protocol):
    async def execute(self, data: BookCreateRequest) -> BookResponse: ...


class GetBooksUseCaseProtocol(Protocol):
    async def execute(self, filters: BooksQuery) -> List[BookResponse]: ...


class FindBookBySlugUseCaseProtocol(Protocol):
    async def execute(self, slug: str) -> BookResponse: ...


class DeleteBookUseCaseProtocol(Protocol):
    async def execute(self, book_id: UUID) -> None: ...


class UpdateBookUseCaseProtocol(Protocol):
    async def execute(self, book_id: UUID, data: BookUpdateRequest) -> BookResponse: ...


class AddFavouriteBookUseCaseProtocol(Protocol):
    async def execute(self, user_id: UUID, slug: str) -> FavouriteBookResponse: ...


class DeleteFavouriteBookUseCaseProtocol(Protocol):
    async def execute(self, user_id: UUID, slug: str) -> None: ...


class FindFavouriteBooksUseCaseProtocol(Protocol):
    async def execute(self, user_id: UUID) -> List[FavouriteBookResponse]: ...


class UpdateFavouriteBookStatusUseCaseProtocol(Protocol):
    async def execute(
            self,
            user_id: UUID,
            slug: str,
            status: BookReadingStatus
    ) -> FavouriteBookResponse: ...