import uuid
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, Text, Integer, func, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.models import SQLBaseModel
from src.infrastructure.database.books.models import BookModel
from src.infrastructure.database.user.models import UserModel


class ReviewModel(SQLBaseModel):
    __tablename__ = "reviews"

    review: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped[UserModel] = relationship("UserModel", back_populates="reviews")
    book: Mapped[BookModel] = relationship("BookModel", back_populates="reviews")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "book_id",
            name="uq_user_book_review"
        ),
    )