from typing import Annotated

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: Annotated[str, Field(description="Почта пользователя", min_length=4)]
    password: Annotated[str, Field(description="Пароль от аккаунта", min_length=4)]
    first_name: Annotated[str, Field(description="Имя пользователя", min_length=1, max_length=10)]
    last_name: Annotated[str, Field(description="Фамилия пользователя", min_length=1, max_length=10)]
    is_admin: Annotated[bool, Field(description="Будет ли пользователь являться админом")]


class LogInRequest(BaseModel):
    email: Annotated[str, Field(description="Почта пользователя")]
    password: Annotated[str, Field(description="Пароль от аккаунта")]