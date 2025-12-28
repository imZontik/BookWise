from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.books.entities import BookEntity


@dataclass
class ReviewEntity:
    id: UUID
    created_at: datetime
    review: str
    rating: int
    full_name: str
    book: BookEntity


@dataclass
class ReviewCreateEntity:
    review: str
    rating: int
    user_id: UUID
    book_id: UUID


@dataclass
class ReviewUpdateEntity:
    review: str
    rating: int
    user_id: UUID
    book_id: UUID
