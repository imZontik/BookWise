from typing import Protocol, Optional
from uuid import UUID

from src.adapters.schemas.requests.user import RegisterRequest, LogInRequest
from src.adapters.schemas.responses.user import UserResponse, TokenResponse
from src.domain.user.entities import UserEntity, UserCreateEntity


class UserRepositoryProtocol(Protocol):
    async def find_by_email(self, email: str) -> Optional[UserEntity]: ...
    async def create(self, entity: UserCreateEntity) -> UserEntity: ...
    async def find_by_id(self, model_id: UUID) -> Optional[UserEntity]: ...


class RegisterUseCaseProtocol(Protocol):
    async def execute(self, data: RegisterRequest) -> UserResponse: ...


class LogInUseCaseProtocol(Protocol):
    async def execute(self, data: LogInRequest) -> TokenResponse: ...