from typing import Annotated

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    review: Annotated[str, Field(description="Отзыв", min_length=10)]
    rating: Annotated[int, Field(description="Оценка", ge=1, le=5)]
