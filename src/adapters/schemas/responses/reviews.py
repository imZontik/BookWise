from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from src.adapters.schemas.responses.books import BookResponse


class ReviewResponse(BaseModel):
    id: Annotated[UUID, Field(description="Уникальный идентификатор отзыва")]
    full_name: Annotated[str, Field(description="Фамилия и имя написавшего отзыв")]
    review: Annotated[str, Field(description="Отзыв", min_length=10)]
    rating: Annotated[int, Field(description="Оценка", ge=1, le=5)]
    book: Annotated[BookResponse, Field(description="Книга")]
    created_at: Annotated[datetime, Field(description="Дата создания")]
