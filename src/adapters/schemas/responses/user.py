from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.user.enums import UserRole


class UserResponse(BaseModel):
    id: Annotated[UUID, Field(description="Уникальный идентификатор пользователя")]
    email: Annotated[str, Field(description="Почта пользователя")]
    first_name: Annotated[str, Field(description="Имя пользователя")]
    last_name: Annotated[str, Field(description="Фамилия пользователя")]
    role: Annotated[UserRole, Field(description="Роль пользователя")]


class TokenResponse(BaseModel):
    access_token: Annotated[str, Field(description="Токен пользователя")]
