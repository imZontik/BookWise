from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AuthorResponse(BaseModel):
    id: Annotated[UUID, Field(description="Уникальный идентификатор")]
    name: Annotated[str, Field(description="Имя и фамилия автора")]
    slug: Annotated[str, Field(description="Slug автора")]

    bio: Annotated[Optional[str], Field(description="Биография")] = None
    birth_date: Annotated[Optional[date], Field(description="Дата рождения")] = None
    death_date: Annotated[Optional[date], Field(description="Дата смерти")] = None
    country: Annotated[Optional[str], Field(description="Страна проживания")] = None
    photo_url: Annotated[Optional[str], Field(description="Фото автора")] = None
