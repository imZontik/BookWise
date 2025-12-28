from typing import List
from uuid import UUID

from src.adapters.schemas.requests.books import BookCreateRequest, BookUpdateRequest, BooksQuery
from src.adapters.schemas.responses.books import BookResponse, FavouriteBookResponse
from src.core.uow import SQLAlchemyUoW
from src.core.utils import generate_slug
from src.domain.author.exceptions import AuthorNotExistException
from src.domain.author.protocols import AuthorRepositoryProtocol
from src.domain.books.entities import BookCreateEntity, BookUpdateEntity, BookFilterEntity
from src.domain.books.enums import BookReadingStatus
from src.domain.books.exceptions import BookNotExistException, FavouriteBookNotExistException
from src.domain.books.mappers import BookSchemaMapper, FavouriteBookSchemaMapper
from src.domain.books.protocols import GetBooksUseCaseProtocol, BookRepositoryProtocol, FindBookBySlugUseCaseProtocol, \
    DeleteBookUseCaseProtocol, CreateBookUseCaseProtocol, UpdateBookUseCaseProtocol, AddFavouriteBookUseCaseProtocol, \
    FavouriteBookRepositoryProtocol, DeleteFavouriteBookUseCaseProtocol, FindFavouriteBooksUseCaseProtocol, \
    UpdateFavouriteBookStatusUseCaseProtocol
from src.domain.cache.protocols import CacheManagerProtocol


class GetBooksUseCase(GetBooksUseCaseProtocol):
    def __init__(
            self,
            mapper: BookSchemaMapper,
            repository: BookRepositoryProtocol
    ):
        self.mapper = mapper
        self.repository = repository

    async def execute(self, filters: BooksQuery) -> List[BookResponse]:
        filters_entity = BookFilterEntity(**filters.model_dump())
        results = await self.repository.find_all(filters=filters_entity)

        return [
            self.mapper.from_entity_to_schema(entity=result)
            for result in results
        ]


class FindBookBySlugUseCase(FindBookBySlugUseCaseProtocol):
    def __init__(
            self,
            mapper: BookSchemaMapper,
            repository: BookRepositoryProtocol,
            cache: CacheManagerProtocol
    ):
        self.mapper = mapper
        self.repository = repository
        self.cache = cache
        self.cache_ttl_seconds = 60

    async def execute(self, slug: str) -> BookResponse:
        cache_key = f"book:slug:{slug}"

        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return BookResponse.model_validate(cached)

        result = await self.repository.find_by_slug(slug=slug)

        if result is None:
            raise BookNotExistException()

        response = self.mapper.from_entity_to_schema(entity=result)

        await self.cache.set_json(
            key=cache_key,
            value=response.model_dump(mode="json"),
            ttl=self.cache_ttl_seconds
        )

        return response


class DeleteBookUseCase(DeleteBookUseCaseProtocol):
    def __init__(
            self,
            repository: BookRepositoryProtocol,
            uow: SQLAlchemyUoW
    ):
        self.repository = repository
        self.uow = uow

    async def execute(self, book_id: UUID) -> None:
        async with self.uow:
            result = await self.repository.delete_by_id(model_id=book_id)

            if not result:
                raise BookNotExistException()


class CreateBookUseCase(CreateBookUseCaseProtocol):
    def __init__(
            self,
            mapper: BookSchemaMapper,
            book_repository: BookRepositoryProtocol,
            author_repository: AuthorRepositoryProtocol,
            uow: SQLAlchemyUoW,
    ):
        self.book_repository = book_repository
        self.author_repository = author_repository
        self.mapper = mapper
        self.uow = uow

    async def execute(self, data: BookCreateRequest) -> BookResponse:
        if data.author_id is not None:
            result = await self.author_repository.find_by_id(model_id=data.author_id)

            if not result:
                raise AuthorNotExistException()

        slug = generate_slug(text=data.title)
        entity = BookCreateEntity(
            title=data.title,
            slug=slug,
            language=data.language,
            description=data.description,
            short_description=data.short_description,
            publish_year=data.publish_year,
            page_count=data.page_count,
            author_id=data.author_id,
            genre=data.genre
        )

        async with self.uow:
            result = await self.book_repository.create(entity=entity)
            return self.mapper.from_entity_to_schema(entity=result)


class UpdateBookUseCase(UpdateBookUseCaseProtocol):
    def __init__(
            self,
            mapper: BookSchemaMapper,
            book_repository: BookRepositoryProtocol,
            author_repository: AuthorRepositoryProtocol,
            uow: SQLAlchemyUoW,
            cache: CacheManagerProtocol
    ):
        self.mapper = mapper
        self.book_repository = book_repository
        self.author_repository = author_repository
        self.uow = uow
        self.cache = cache

    async def execute(self, book_id: UUID, data: BookUpdateRequest) -> BookResponse:
        if data.author_id is not None:
            result = await self.author_repository.find_by_id(model_id=data.author_id)

            if not result:
                raise AuthorNotExistException()

        entity = BookUpdateEntity(
            id=book_id,
            language=data.language,
            description=data.description,
            short_description=data.short_description,
            publish_year=data.publish_year,
            page_count=data.page_count,
            author_id=data.author_id,
            genre=data.genre
        )

        async with self.uow:
            result = await self.book_repository.update(entity=entity)

            if result is None:
                raise BookNotExistException()

            cache_key = f"book:slug:{result.slug}"
            await self.cache.delete(key=cache_key)

            return self.mapper.from_entity_to_schema(entity=result)


class AddFavouriteBookUseCase(AddFavouriteBookUseCaseProtocol):
    def __init__(
            self,
            mapper: FavouriteBookSchemaMapper,
            book_repository: BookRepositoryProtocol,
            favourite_book_repository: FavouriteBookRepositoryProtocol,
            uow: SQLAlchemyUoW
    ):
        self.mapper = mapper
        self.book_repository = book_repository
        self.favourite_book_repository = favourite_book_repository
        self.uow = uow

    async def execute(self, user_id: UUID, slug: str) -> FavouriteBookResponse:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            raise BookNotExistException()

        async with self.uow:
            result = await self.favourite_book_repository.add(
                user_id=user_id,
                book_id=book.id
            )

            return self.mapper.from_entity_to_schema(entity=result)


class DeleteFavouriteBookUseCase(DeleteFavouriteBookUseCaseProtocol):
    def __init__(
            self,
            book_repository: BookRepositoryProtocol,
            favourite_book_repository: FavouriteBookRepositoryProtocol,
            uow: SQLAlchemyUoW
    ):
        self.book_repository = book_repository
        self.favourite_book_repository = favourite_book_repository
        self.uow = uow

    async def execute(self, user_id: UUID, slug: str) -> None:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            raise BookNotExistException()

        async with self.uow:
            result = await self.favourite_book_repository.delete(
                user_id=user_id,
                book_id=book.id
            )

            if not result:
                raise FavouriteBookNotExistException()


class FindFavouriteBooksUseCase(FindFavouriteBooksUseCaseProtocol):
    def __init__(
            self,
            mapper: FavouriteBookSchemaMapper,
            repository: FavouriteBookRepositoryProtocol
    ):
        self.mapper = mapper
        self.repository = repository

    async def execute(self, user_id: UUID) -> List[FavouriteBookResponse]:
        entities = await self.repository.find_all(user_id=user_id)

        return [
            self.mapper.from_entity_to_schema(entity=entity)
            for entity in entities
        ]


class UpdateFavouriteBookStatusUseCase(UpdateFavouriteBookStatusUseCaseProtocol):
    def __init__(
            self,
            mapper: FavouriteBookSchemaMapper,
            book_repository: BookRepositoryProtocol,
            favourite_book_repository: FavouriteBookRepositoryProtocol,
            uow: SQLAlchemyUoW
    ):
        self.mapper = mapper
        self.book_repository = book_repository
        self.favourite_book_repository = favourite_book_repository
        self.uow = uow

    async def execute(
            self,
            user_id: UUID,
            slug: str,
            status: BookReadingStatus
    ) -> FavouriteBookResponse:
        book = await self.book_repository.find_by_slug(slug=slug)

        if book is None:
            raise BookNotExistException()

        async with self.uow:
            result = await self.favourite_book_repository.update_status(
                user_id=user_id,
                book_id=book.id,
                status=status
            )

            if result is None:
                raise FavouriteBookNotExistException()

            return self.mapper.from_entity_to_schema(entity=result)
