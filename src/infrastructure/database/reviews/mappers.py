from src.core.mappers import ModelToEntityMapper
from src.domain.reviews.entities import ReviewEntity
from src.infrastructure.database.books.mappers import BookModelMapper
from src.infrastructure.database.reviews.models import ReviewModel


class ReviewModelMapper(ModelToEntityMapper[ReviewModel, ReviewEntity]):
    def __init__(
            self,
            mapper: BookModelMapper
    ):
        self.mapper = mapper

    def from_model_to_entity(self, model: ReviewModel) -> ReviewEntity:
        return ReviewEntity(
            id=model.id,
            review=model.review,
            rating=model.rating,
            full_name=f"{model.user.first_name} {model.user.last_name}",
            book=self.mapper.from_model_to_entity(model=model.book),
            created_at=model.created_at
        )
