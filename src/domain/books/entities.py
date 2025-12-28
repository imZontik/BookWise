from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.domain.books.enums import Genre, BookReadingStatus


@dataclass
class BookEntity:
    id: UUID
    title: str
    slug: str
    language: str
    genre: Genre
    description: Optional[str] = None
    short_description: Optional[str] = None
    publish_year: Optional[int] = None
    page_count: Optional[int] = None
    author_id: Optional[UUID] = None


@dataclass
class BookCreateEntity:
    title: str
    slug: str
    language: str
    genre: Genre
    description: Optional[str] = None
    short_description: Optional[str] = None
    publish_year: Optional[int] = None
    page_count: Optional[int] = None
    author_id: Optional[UUID] = None


@dataclass
class BookUpdateEntity:
    id: UUID
    language: str
    genre: Genre
    description: Optional[str] = None
    short_description: Optional[str] = None
    publish_year: Optional[int] = None
    page_count: Optional[int] = None
    author_id: Optional[UUID] = None


@dataclass
class BookFilterEntity:
    genre: Optional[Genre] = None
    limit: Optional[int] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    pages_from: Optional[int] = None
    pages_to: Optional[int] = None


@dataclass
class FavouriteBookEntity:
    id: UUID
    status: BookReadingStatus
    book: BookEntity