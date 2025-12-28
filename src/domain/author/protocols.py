from typing import Protocol, Optional
from uuid import UUID

from fastapi import UploadFile

from src.adapters.schemas.requests.author import AuthorCreateRequest
from src.adapters.schemas.responses.author import AuthorResponse
from src.domain.author.entities import AuthorCreateEntity, AuthorEntity


class AuthorRepositoryProtocol(Protocol):
    async def create(self, entity: AuthorCreateEntity) -> AuthorEntity: ...
    async def find_by_slug(self, slug: str) -> Optional[AuthorEntity]: ...
    async def find_by_id(self, model_id: UUID) -> Optional[AuthorEntity]: ...
    async def delete_by_id(self, model_id: UUID) -> bool: ...
    async def update_photo_url(self, model_id: UUID, photo_url: str) -> AuthorEntity: ...


class CreateAuthorUseCaseProtocol(Protocol):
    async def execute(self, data: AuthorCreateRequest) -> AuthorResponse: ...


class FindAuthorUseCaseProtocol(Protocol):
    async def execute(self, slug: str) -> AuthorResponse: ...


class DeleteAuthorUseCaseProtocol(Protocol):
    async def execute(self, author_id: UUID) -> None: ...


class UpdateAuthorPhotoUseCaseProtocol(Protocol):
    async def execute(self, author_id: UUID, file: UploadFile) -> AuthorResponse: ...