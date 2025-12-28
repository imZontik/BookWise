import uuid
from typing import Optional

from sqlalchemy import String, Enum, Text, Integer, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.models import SQLBaseModel
from src.domain.books.enums import Genre, BookReadingStatus


class BookModel(SQLBaseModel):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    language: Mapped[str] = mapped_column(String(25), nullable=True, default="Русский")
    genre: Mapped[Genre] = mapped_column(
        Enum(Genre, native_enum=False),
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publish_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authors.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    reviews = relationship("ReviewModel", back_populates="book")


class FavouriteBookModel(SQLBaseModel):
    __tablename__ = "favourite_books"

    status: Mapped[BookReadingStatus] = mapped_column(
        Enum(BookReadingStatus, native_enum=False),
        nullable=False,
        default=BookReadingStatus.NOT_STARTED
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )

    book = relationship("BookModel")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "book_id",
            name="uq_user_book_favourite"
        ),
    )