from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, Field


class AuthorCreateRequest(BaseModel):
    name: Annotated[str, Field(description="Имя и фамилия автора")]

    bio: Annotated[Optional[str], Field(description="Биография")] = None
    birth_date: Annotated[Optional[date], Field(description="Дата рождения")] = None
    death_date: Annotated[Optional[date], Field(description="Дата смерти")] = None
    country: Annotated[Optional[str], Field(description="Страна проживания")] = None
