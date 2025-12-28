from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.domain.books.enums import Genre, BookReadingStatus


class BookCreateRequest(BaseModel):
    title: Annotated[str, Field(description="Название книги")]
    genre: Annotated[Genre, Field(description="Жанр книги")]

    language: Annotated[Optional[str], Field(description="На каком языке написана книга")] = None
    description: Annotated[Optional[str], Field(description="Содержание книги")] = None
    short_description: Annotated[Optional[str], Field(description="Краткое содержание")] = None
    publish_year: Annotated[Optional[int], Field(description="Год выпуска")] = None
    page_count: Annotated[Optional[int], Field(description="Количество страниц")] = None
    author_id: Annotated[Optional[UUID], Field(description="Айди автора, написавшего книгу")] = None


class BookUpdateRequest(BaseModel):
    genre: Annotated[Genre, Field(description="Жанр книги")]

    language: Annotated[Optional[str], Field(description="На каком языке написана книга")] = None
    description: Annotated[Optional[str], Field(description="Содержание книги")] = None
    short_description: Annotated[Optional[str], Field(description="Краткое содержание")] = None
    publish_year: Annotated[Optional[int], Field(description="Год выпуска")] = None
    page_count: Annotated[Optional[int], Field(description="Количество страниц")] = None
    author_id: Annotated[Optional[UUID], Field(description="Айди автора, написавшего книгу")] = None


class BooksQuery(BaseModel):
    genre: Annotated[Optional[Genre], Field(description="Жанр книги")] = None
    limit: Annotated[Optional[int], Field(ge=0, description="Максимальное кол-во книг, которые выведется")] = None
    year_from: Annotated[Optional[int], Field(ge=0, description="Минимальный год публикации")] = None
    year_to: Annotated[Optional[int], Field(ge=0, description="Максимальный год публикации")] = None
    pages_from: Annotated[Optional[int], Field(ge=1, description="Минимальное кол-во страниц")] = None
    pages_to: Annotated[Optional[int], Field(ge=1, description="Максимальное кол-во страниц")] = None

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.year_from is not None and self.year_to is not None and self.year_from > self.year_to:
            raise ValueError("Минимальный год не может быть больше максимального года публикации")

        if self.pages_from is not None and self.pages_to is not None and self.pages_from > self.pages_to:
            raise ValueError("Минимальное кол-во страниц не может быть больше максимального кол-ва страниц")

        return self


class FavouriteBookUpdateStatusRequest(BaseModel):
    status: Annotated[BookReadingStatus, Field(description="Статус прочтения книги")]