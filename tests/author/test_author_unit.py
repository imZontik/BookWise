import uuid
from unittest.mock import create_autospec, AsyncMock

import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.schemas.requests.author import AuthorCreateRequest
from src.adapters.schemas.responses.author import AuthorResponse
from src.application.usecases.author import FindAuthorUseCase, CreateAuthorUseCase, DeleteAuthorUseCase, \
    UpdateAuthorPhotoUseCase
from src.core.config import settings
from src.core.uow import SQLAlchemyUoW
from src.domain.author.entities import AuthorEntity, AuthorCreateEntity
from src.domain.author.exceptions import AuthorNotExistException, AuthorAlreadyExistException
from src.domain.author.mappers import AuthorSchemaMapper
from src.domain.cache.protocols import CacheManagerProtocol
from src.domain.storage.file_storage import MinioClientProtocol
from src.domain.user.protocols import UserRepositoryProtocol


@pytest.mark.asyncio
class TestFindAuthorUseCase:
    async def test_execute_success(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.find_by_slug = AsyncMock()

        mapper = create_autospec(AuthorSchemaMapper, instance=True)
        founded_result = create_autospec(AuthorResponse, instance=True)
        founded_result.model_dump.return_value = object()
        slug = "thomas-shelby"

        cache_manager = create_autospec(CacheManagerProtocol, instance=True)
        cache_manager.get.return_value = None

        author_entity = AuthorEntity(
            id=uuid.uuid4(),
            name="Thomas Shelby",
            slug=slug,
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
            photo_url=None
        )

        repository.find_by_slug.return_value = author_entity
        mapper.from_entity_to_schema.return_value = founded_result

        use_case = FindAuthorUseCase(
            repository=repository,
            mapper=mapper,
            cache=cache_manager
        )

        result = await use_case.execute(slug=slug)
        assert result == founded_result

        repository.find_by_slug.assert_awaited_once_with(slug=slug)
        mapper.from_entity_to_schema.assert_called_once_with(entity=author_entity)

    async def test_execute_author_not_found(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.find_by_slug = AsyncMock()

        mapper = create_autospec(AuthorSchemaMapper, instance=True)
        repository.find_by_slug.return_value = None
        slug = "thomas-shelby"

        cache_manager = create_autospec(CacheManagerProtocol, instance=True)
        cache_manager.get.return_value = None

        use_case = FindAuthorUseCase(
            repository=repository,
            mapper=mapper,
            cache=cache_manager
        )

        with pytest.raises(AuthorNotExistException):
            await use_case.execute(slug=slug)

        repository.find_by_slug.assert_awaited_once_with(slug=slug)
        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestCreateAuthorUseCase:
    async def test_execute_success(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.create = AsyncMock()

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        mapper = create_autospec(AuthorSchemaMapper, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        slug = "thomas-shelby"
        author_entity = AuthorEntity(
            id=uuid.uuid4(),
            name="Thomas Shelby",
            slug=slug,
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
            photo_url=None
        )

        create_author_entity = AuthorCreateEntity(
            name="Thomas Shelby",
            slug=slug,
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
        )

        request = AuthorCreateRequest(
            name="Thomas Shelby",
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
        )

        created_author = object()

        mapper.from_entity_to_schema.return_value = author_entity
        repository.create.return_value = created_author

        use_case = CreateAuthorUseCase(
            repository=repository,
            uow=uow,
            mapper=mapper
        )

        author = await use_case.execute(data=request)
        assert author == author_entity
        assert author.slug == slug

        repository.create.assert_awaited_once_with(entity=create_author_entity)
        mapper.from_entity_to_schema.assert_called_once_with(entity=created_author)

    async def test_execute_author_exist(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.create = AsyncMock(side_effect=AuthorAlreadyExistException())

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        mapper = create_autospec(AuthorSchemaMapper, instance=True)
        uow = SQLAlchemyUoW(fake_session)
        slug = "thomas-shelby"

        create_author_entity = AuthorCreateEntity(
            name="Thomas Shelby",
            slug=slug,
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
        )

        request = AuthorCreateRequest(
            name="Thomas Shelby",
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
        )

        use_case = CreateAuthorUseCase(
            repository=repository,
            uow=uow,
            mapper=mapper
        )

        with pytest.raises(AuthorAlreadyExistException):
            await use_case.execute(data=request)

        mapper.from_entity_to_schema.assert_not_called()
        repository.create.assert_awaited_once_with(entity=create_author_entity)


@pytest.mark.asyncio
class TestDeleteAuthorUseCase:
    async def test_execute_success(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.delete_by_id = AsyncMock()

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        uow = SQLAlchemyUoW(fake_session)
        author_id = uuid.uuid4()

        repository.delete_by_id.return_value = True

        use_case = DeleteAuthorUseCase(
            repository=repository,
            uow=uow
        )

        await use_case.execute(author_id=author_id)
        repository.delete_by_id.assert_awaited_once_with(model_id=author_id)

    async def test_execute_author_not_found(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.delete_by_id = AsyncMock()

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        uow = SQLAlchemyUoW(fake_session)
        author_id = uuid.uuid4()

        repository.delete_by_id.return_value = False

        use_case = DeleteAuthorUseCase(
            repository=repository,
            uow=uow
        )

        with pytest.raises(AuthorNotExistException):
            await use_case.execute(author_id=author_id)

        repository.delete_by_id.assert_awaited_once_with(model_id=author_id)


@pytest.mark.asyncio
class TestUpdateAuthorPhotoUseCase:
    async def test_execute_success(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.update_photo_url = AsyncMock()
        repository.find_by_id = AsyncMock()

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        mapper = create_autospec(AuthorSchemaMapper, instance=True)
        storage = create_autospec(MinioClientProtocol, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        author_id = uuid.uuid4()
        upload_file = create_autospec(UploadFile, instance=True)
        public_url = "http://test.com"

        use_case = UpdateAuthorPhotoUseCase(
            repository=repository,
            uow=uow,
            mapper=mapper,
            storage=storage,
            cache=cache_manager
        )

        author_entity = AuthorEntity(
            id=author_id,
            name="Thomas Shelby",
            slug="thomas-shelby",
            bio=None,
            birth_date=None,
            death_date=None,
            country=None,
            photo_url=public_url
        )

        updated_author = object()

        author_founded_by_id = create_autospec(AuthorEntity, instance=True)
        author_founded_by_id.photo_url = None
        author_founded_by_id.slug = "test"

        mapper.from_entity_to_schema.return_value = author_entity
        storage.save_file.return_value = public_url
        repository.find_by_id.return_value = author_founded_by_id
        repository.update_photo_url.return_value = updated_author

        result = await use_case.execute(
            author_id=author_id,
            file=upload_file
        )

        assert result == author_entity

        storage.delete_file.assert_not_called()
        storage.save_file.assert_awaited_once_with(
            file=upload_file,
            bucket_name=settings.MINIO_BUCKET_AVATARS,
            public=True
        )

        repository.find_by_id.assert_awaited_once_with(model_id=author_id)
        repository.update_photo_url.assert_awaited_once_with(
            model_id=author_id,
            photo_url=public_url
        )

        mapper.from_entity_to_schema.assert_called_once_with(entity=updated_author)

    async def test_execute_author_not_found(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.update_photo_url = AsyncMock()
        repository.find_by_id = AsyncMock()

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        mapper = create_autospec(AuthorSchemaMapper, instance=True)
        storage = create_autospec(MinioClientProtocol, instance=True)
        uow = SQLAlchemyUoW(fake_session)

        cache_manager = create_autospec(CacheManagerProtocol, instance=True)

        author_id = uuid.uuid4()
        upload_file = create_autospec(UploadFile, instance=True)

        use_case = UpdateAuthorPhotoUseCase(
            repository=repository,
            uow=uow,
            mapper=mapper,
            storage=storage,
            cache=cache_manager
        )

        repository.find_by_id.return_value = None

        with pytest.raises(AuthorNotExistException):
            await use_case.execute(
                author_id=author_id,
                file=upload_file
            )

        repository.find_by_id.assert_awaited_once_with(model_id=author_id)
        repository.update_photo_url.assert_not_awaited()

        storage.save_file.assert_not_awaited()
        storage.delete_file.assert_not_awaited()

        mapper.from_entity_to_schema.assert_not_called()
