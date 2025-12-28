from uuid import UUID

from fastapi import UploadFile

from src.adapters.schemas.requests.author import AuthorCreateRequest
from src.adapters.schemas.responses.author import AuthorResponse
from src.core.config import settings
from src.core.uow import SQLAlchemyUoW
from src.core.utils import generate_slug
from src.domain.author.entities import AuthorCreateEntity
from src.domain.author.exceptions import AuthorNotExistException
from src.domain.author.mappers import AuthorSchemaMapper
from src.domain.author.protocols import CreateAuthorUseCaseProtocol, FindAuthorUseCaseProtocol, \
    DeleteAuthorUseCaseProtocol, UpdateAuthorPhotoUseCaseProtocol, AuthorRepositoryProtocol
from src.domain.cache.protocols import CacheManagerProtocol
from src.domain.storage.exceptions import MinioFileDeleteException
from src.domain.storage.file_storage import MinioClientProtocol


class FindAuthorUseCase(FindAuthorUseCaseProtocol):
    def __init__(
            self,
            repository: AuthorRepositoryProtocol,
            mapper: AuthorSchemaMapper,
            cache: CacheManagerProtocol
    ):
        self.repository = repository
        self.mapper = mapper
        self.cache = cache
        self.cache_ttl_seconds = 120

    async def execute(self, slug: str) -> AuthorResponse:
        cache_key = f"author:slug:{slug}"
        cached = await self.cache.get(cache_key)

        if cached is not None:
            return AuthorResponse.model_validate(cached)

        result = await self.repository.find_by_slug(slug=slug)

        if result is None:
            raise AuthorNotExistException()

        response = self.mapper.from_entity_to_schema(entity=result)

        await self.cache.set_json(
            key=cache_key,
            value=response.model_dump(mode="json"),
            ttl=self.cache_ttl_seconds
        )

        return response


class CreateAuthorUseCase(CreateAuthorUseCaseProtocol):
    def __init__(
            self,
            repository: AuthorRepositoryProtocol,
            uow: SQLAlchemyUoW,
            mapper: AuthorSchemaMapper
    ):
        self.repository = repository
        self.uow = uow
        self.mapper = mapper

    async def execute(self, data: AuthorCreateRequest) -> AuthorResponse:
        slug = generate_slug(text=data.name)
        entity = AuthorCreateEntity(
            name=data.name,
            slug=slug,
            bio=data.bio,
            birth_date=data.birth_date,
            death_date=data.death_date,
            country=data.country
        )

        async with self.uow:
            result = await self.repository.create(entity=entity)
            return self.mapper.from_entity_to_schema(entity=result)


class DeleteAuthorUseCase(DeleteAuthorUseCaseProtocol):
    def __init__(
            self,
            repository: AuthorRepositoryProtocol,
            uow: SQLAlchemyUoW
    ):
        self.repository = repository
        self.uow = uow

    async def execute(self, author_id: UUID) -> None:
        async with self.uow:
            result = await self.repository.delete_by_id(model_id=author_id)

            if not result:
                raise AuthorNotExistException()


class UpdateAuthorPhotoUseCase(UpdateAuthorPhotoUseCaseProtocol):
    def __init__(
            self,
            repository: AuthorRepositoryProtocol,
            uow: SQLAlchemyUoW,
            mapper: AuthorSchemaMapper,
            storage: MinioClientProtocol,
            cache: CacheManagerProtocol
    ):
        self.repository = repository
        self.uow = uow
        self.mapper = mapper
        self.storage = storage
        self.cache = cache

    async def execute(self, author_id: UUID, file: UploadFile) -> AuthorResponse:
        async with self.uow:
            author = await self.repository.find_by_id(model_id=author_id)

            if author is None:
                raise AuthorNotExistException()

            author_photo_url = author.photo_url
            public_url = await self.storage.save_file(
                file=file,
                bucket_name=settings.MINIO_BUCKET_AVATARS,
                public=True
            )

            result = await self.repository.update_photo_url(
                model_id=author_id,
                photo_url=public_url
            )

        if author_photo_url is not None:
            try:
                await self.storage.delete_file(author_photo_url)
            except MinioFileDeleteException:
                pass

        cache_key = f"author:slug:{author.slug}"
        await self.cache.delete(key=cache_key)

        return self.mapper.from_entity_to_schema(entity=result)
