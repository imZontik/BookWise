from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.books.enums import Genre, BookReadingStatus


class BookResponse(BaseModel):
    id: Annotated[UUID, Field(description="Уникальный идентификатор книги")]
    title: Annotated[str, Field(description="Название книги")]
    slug: Annotated[str, Field(description="Slug книги")]
    genre: Annotated[Genre, Field(description="Жанр книги")]
    language: Annotated[str, Field(description="На каком языке написана книга")]

    description: Annotated[Optional[str], Field(description="Содержание книги")] = None
    short_description: Annotated[Optional[str], Field(description="Краткое содержание")] = None
    publish_year: Annotated[Optional[int], Field(description="Год выпуска")] = None
    page_count: Annotated[Optional[int], Field(description="Количество страниц")] = None
    author_id: Annotated[Optional[UUID], Field(description="Айди автора, написавшего книгу")] = None


class FavouriteBookResponse(BaseModel):
    id: Annotated[UUID, Field(description="Уникальный идентификатор книги")]
    status: Annotated[BookReadingStatus, Field(description="Статус прочтения книги")]
    book: Annotated[BookResponse, Field(description="Информация о книге")]