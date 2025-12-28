from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.usecases.author import FindAuthorUseCase, CreateAuthorUseCase, DeleteAuthorUseCase, \
    UpdateAuthorPhotoUseCase
from src.application.usecases.books import GetBooksUseCase, FindBookBySlugUseCase, DeleteBookUseCase, CreateBookUseCase, \
    UpdateBookUseCase, AddFavouriteBookUseCase, DeleteFavouriteBookUseCase, FindFavouriteBooksUseCase, \
    UpdateFavouriteBookStatusUseCase
from src.application.usecases.reviews import CreateReviewUseCase, FindReviewsUseCase, UpdateReviewUseCase, \
    DeleteReviewUseCase
from src.application.usecases.user import RegisterUseCase, LogInUseCase
from src.core.database.database import get_session, get_uow
from src.core.uow import SQLAlchemyUoW
from src.domain.author.mappers import AuthorSchemaMapper
from src.domain.author.protocols import AuthorRepositoryProtocol, FindAuthorUseCaseProtocol, \
    CreateAuthorUseCaseProtocol, DeleteAuthorUseCaseProtocol, UpdateAuthorPhotoUseCaseProtocol
from src.domain.books.mappers import BookSchemaMapper, FavouriteBookSchemaMapper
from src.domain.books.protocols import BookRepositoryProtocol, GetBooksUseCaseProtocol, FindBookBySlugUseCaseProtocol, \
    DeleteBookUseCaseProtocol, CreateBookUseCaseProtocol, UpdateBookUseCaseProtocol, FavouriteBookRepositoryProtocol, \
    AddFavouriteBookUseCaseProtocol, DeleteFavouriteBookUseCaseProtocol, FindFavouriteBooksUseCaseProtocol, \
    UpdateFavouriteBookStatusUseCaseProtocol
from src.domain.cache.protocols import CacheManagerProtocol
from src.domain.reviews.mappers import ReviewSchemaMapper
from src.domain.reviews.protocols import ReviewRepositoryProtocol, CreateReviewUseCaseProtocol, \
    FindReviewsUseCaseProtocol, UpdateReviewUseCaseProtocol, DeleteReviewUseCaseProtocol
from src.domain.security.protocols import PasswordHasherProtocol, TokenServiceProtocol
from src.domain.storage.file_storage import MinioClientProtocol
from src.domain.user.mappers import UserSchemaMapper
from src.domain.user.protocols import UserRepositoryProtocol, RegisterUseCaseProtocol
from src.infrastructure.cache.cache import get_redis_cache_manager
from src.infrastructure.database.author.mappers import AuthorModelMapper
from src.infrastructure.database.author.repositories import AuthorRepository
from src.infrastructure.database.books.mappers import BookModelMapper, FavouriteBookModelMapper
from src.infrastructure.database.books.repositories import BookRepository, FavouriteBookRepository
from src.infrastructure.database.reviews.mappers import ReviewModelMapper
from src.infrastructure.database.reviews.repositories import ReviewRepository
from src.infrastructure.database.user.mappers import UserModelMapper
from src.infrastructure.database.user.repositories import UserRepository
from src.infrastructure.security.security import PasswordHasher, TokenService
from src.infrastructure.storage.file_storage import MinioClient


def get_user_model_mapper() -> UserModelMapper:
    return UserModelMapper()


def get_user_schema_mapper() -> UserSchemaMapper:
    return UserSchemaMapper()


def get_author_model_mapper() -> AuthorModelMapper:
    return AuthorModelMapper()


def get_author_schema_mapper() -> AuthorSchemaMapper:
    return AuthorSchemaMapper()


def get_book_model_mapper() -> BookModelMapper:
    return BookModelMapper()


def get_book_schema_mapper() -> BookSchemaMapper:
    return BookSchemaMapper()


def get_review_model_mapper(
        mapper: BookModelMapper = Depends(get_book_model_mapper)
) -> ReviewModelMapper:
    return ReviewModelMapper(mapper=mapper)


def get_review_schema_mapper(
        mapper: BookSchemaMapper = Depends(get_book_schema_mapper)
) -> ReviewSchemaMapper:
    return ReviewSchemaMapper(mapper=mapper)


def get_favourite_book_model_mapper(
        mapper: BookModelMapper = Depends(get_book_model_mapper)
) -> FavouriteBookModelMapper:
    return FavouriteBookModelMapper(mapper=mapper)


def get_favourite_book_schema_mapper(
        mapper: BookSchemaMapper = Depends(get_book_schema_mapper)
) -> FavouriteBookSchemaMapper:
    return FavouriteBookSchemaMapper(mapper=mapper)


def get_password_hasher() -> PasswordHasherProtocol:
    return PasswordHasher()


def get_token_service() -> TokenServiceProtocol:
    return TokenService()


def get_minio_client() -> MinioClientProtocol:
    return MinioClient()


def get_user_repository(
        session: AsyncSession = Depends(get_session),
        mapper: UserModelMapper = Depends(get_user_model_mapper)
) -> UserRepositoryProtocol:
    return UserRepository(
        session=session,
        mapper=mapper
    )


def get_register_use_case(
        repository: UserRepositoryProtocol = Depends(get_user_repository),
        mapper: UserSchemaMapper = Depends(get_user_schema_mapper),
        password_hasher: PasswordHasherProtocol = Depends(get_password_hasher),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> RegisterUseCaseProtocol:
    return RegisterUseCase(
        repository=repository,
        mapper=mapper,
        password_hasher=password_hasher,
        uow=uow
    )


def get_log_in_use_case(
        repository: UserRepositoryProtocol = Depends(get_user_repository),
        password_hasher: PasswordHasherProtocol = Depends(get_password_hasher),
        token_service: TokenServiceProtocol = Depends(get_token_service)
):
    return LogInUseCase(
        repository=repository,
        password_hasher=password_hasher,
        token_service=token_service
    )


def get_author_repository(
        session: AsyncSession = Depends(get_session),
        mapper: AuthorModelMapper = Depends(get_author_model_mapper)
) -> AuthorRepositoryProtocol:
    return AuthorRepository(
        session=session,
        mapper=mapper
    )


def get_find_author_use_case(
        repository: AuthorRepositoryProtocol = Depends(get_author_repository),
        mapper: AuthorSchemaMapper = Depends(get_author_schema_mapper),
        cache: CacheManagerProtocol = Depends(get_redis_cache_manager)
) -> FindAuthorUseCaseProtocol:
    return FindAuthorUseCase(
        repository=repository,
        mapper=mapper,
        cache=cache
    )


def get_create_author_use_case(
        repository: AuthorRepositoryProtocol = Depends(get_author_repository),
        mapper: AuthorSchemaMapper = Depends(get_author_schema_mapper),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> CreateAuthorUseCaseProtocol:
    return CreateAuthorUseCase(
        repository=repository,
        mapper=mapper,
        uow=uow
    )


def get_delete_author_use_case(
        repository: AuthorRepositoryProtocol = Depends(get_author_repository),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> DeleteAuthorUseCaseProtocol:
    return DeleteAuthorUseCase(
        repository=repository,
        uow=uow
    )


def get_update_author_photo_use_case(
        repository: AuthorRepositoryProtocol = Depends(get_author_repository),
        mapper: AuthorSchemaMapper = Depends(get_author_schema_mapper),
        uow: SQLAlchemyUoW = Depends(get_uow),
        storage: MinioClientProtocol = Depends(get_minio_client),
        cache: CacheManagerProtocol = Depends(get_redis_cache_manager)
) -> UpdateAuthorPhotoUseCaseProtocol:
    return UpdateAuthorPhotoUseCase(
        repository=repository,
        mapper=mapper,
        uow=uow,
        storage=storage,
        cache=cache
    )


def get_book_repository(
        session: AsyncSession = Depends(get_session),
        mapper: BookModelMapper = Depends(get_book_model_mapper)
) -> BookRepositoryProtocol:
    return BookRepository(
        session=session,
        mapper=mapper
    )


def get_get_books_use_case(
        mapper: BookSchemaMapper = Depends(get_book_schema_mapper),
        repository: BookRepositoryProtocol = Depends(get_book_repository)
) -> GetBooksUseCaseProtocol:
    return GetBooksUseCase(
        repository=repository,
        mapper=mapper
    )


def get_find_book_by_slug_use_case(
        mapper: BookSchemaMapper = Depends(get_book_schema_mapper),
        repository: BookRepositoryProtocol = Depends(get_book_repository),
        cache: CacheManagerProtocol = Depends(get_redis_cache_manager)
) -> FindBookBySlugUseCaseProtocol:
    return FindBookBySlugUseCase(
        repository=repository,
        mapper=mapper,
        cache=cache
    )


def get_delete_book_use_case(
        uow: SQLAlchemyUoW = Depends(get_uow),
        repository: BookRepositoryProtocol = Depends(get_book_repository)
) -> DeleteBookUseCaseProtocol:
    return DeleteBookUseCase(
        uow=uow,
        repository=repository
    )


def get_create_book_use_case(
        uow: SQLAlchemyUoW = Depends(get_uow),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        author_repository: AuthorRepositoryProtocol = Depends(get_author_repository),
        mapper: BookSchemaMapper = Depends(get_book_schema_mapper)
) -> CreateBookUseCaseProtocol:
    return CreateBookUseCase(
        uow=uow,
        book_repository=book_repository,
        author_repository=author_repository,
        mapper=mapper
    )


def get_update_book_use_case(
        uow: SQLAlchemyUoW = Depends(get_uow),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        author_repository: AuthorRepositoryProtocol = Depends(get_author_repository),
        mapper: BookSchemaMapper = Depends(get_book_schema_mapper),
        cache: CacheManagerProtocol = Depends(get_redis_cache_manager)
) -> UpdateBookUseCaseProtocol:
    return UpdateBookUseCase(
        uow=uow,
        book_repository=book_repository,
        author_repository=author_repository,
        mapper=mapper,
        cache=cache
    )


def get_review_repository(
        session: AsyncSession = Depends(get_session),
        mapper: ReviewModelMapper = Depends(get_review_model_mapper)
) -> ReviewRepositoryProtocol:
    return ReviewRepository(
        session=session,
        mapper=mapper
    )


def get_create_review_use_case(
        review_repository: ReviewRepositoryProtocol = Depends(get_review_repository),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        mapper: ReviewSchemaMapper = Depends(get_review_schema_mapper),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> CreateReviewUseCaseProtocol:
    return CreateReviewUseCase(
        review_repository=review_repository,
        book_repository=book_repository,
        mapper=mapper,
        uow=uow
    )


def get_find_reviews_use_case(
        review_repository: ReviewRepositoryProtocol = Depends(get_review_repository),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        mapper: ReviewSchemaMapper = Depends(get_review_schema_mapper)
) -> FindReviewsUseCaseProtocol:
    return FindReviewsUseCase(
        review_repository=review_repository,
        book_repository=book_repository,
        mapper=mapper
    )


def get_update_review_use_case(
        review_repository: ReviewRepositoryProtocol = Depends(get_review_repository),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        mapper: ReviewSchemaMapper = Depends(get_review_schema_mapper),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> UpdateReviewUseCaseProtocol:
    return UpdateReviewUseCase(
        review_repository=review_repository,
        book_repository=book_repository,
        mapper=mapper,
        uow=uow
    )


def get_delete_review_use_case(
        review_repository: ReviewRepositoryProtocol = Depends(get_review_repository),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> DeleteReviewUseCaseProtocol:
    return DeleteReviewUseCase(
        review_repository=review_repository,
        book_repository=book_repository,
        uow=uow
    )


def get_favourite_book_repository(
        session: AsyncSession = Depends(get_session),
        mapper: FavouriteBookModelMapper = Depends(get_favourite_book_model_mapper)
) -> FavouriteBookRepositoryProtocol:
    return FavouriteBookRepository(
        session=session,
        mapper=mapper
    )


def get_add_favourite_book_use_case(
        mapper: FavouriteBookSchemaMapper = Depends(get_favourite_book_schema_mapper),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        favourite_book_repository: FavouriteBookRepositoryProtocol = Depends(get_favourite_book_repository),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> AddFavouriteBookUseCaseProtocol:
    return AddFavouriteBookUseCase(
        mapper=mapper,
        book_repository=book_repository,
        favourite_book_repository=favourite_book_repository,
        uow=uow
    )


def get_delete_favourite_book_use_case(
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        favourite_book_repository: FavouriteBookRepositoryProtocol = Depends(get_favourite_book_repository),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> DeleteFavouriteBookUseCaseProtocol:
    return DeleteFavouriteBookUseCase(
        book_repository=book_repository,
        favourite_book_repository=favourite_book_repository,
        uow=uow
    )


def get_find_favourite_books_use_case(
        mapper: FavouriteBookSchemaMapper = Depends(get_favourite_book_schema_mapper),
        repository: FavouriteBookRepositoryProtocol = Depends(get_favourite_book_repository)
) -> FindFavouriteBooksUseCaseProtocol:
    return FindFavouriteBooksUseCase(
        mapper=mapper,
        repository=repository
    )


def get_update_favourite_book_status_use_case(
        mapper: FavouriteBookSchemaMapper = Depends(get_favourite_book_schema_mapper),
        book_repository: BookRepositoryProtocol = Depends(get_book_repository),
        favourite_book_repository: FavouriteBookRepositoryProtocol = Depends(get_favourite_book_repository),
        uow: SQLAlchemyUoW = Depends(get_uow)
) -> UpdateFavouriteBookStatusUseCaseProtocol:
    return UpdateFavouriteBookStatusUseCase(
        mapper=mapper,
        book_repository=book_repository,
        favourite_book_repository=favourite_book_repository,
        uow=uow
    )