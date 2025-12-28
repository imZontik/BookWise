from src.adapters.schemas.responses.reviews import ReviewResponse
from src.core.mappers import EntityToSchemaMapper
from src.domain.books.mappers import BookSchemaMapper
from src.domain.reviews.entities import ReviewEntity


class ReviewSchemaMapper(EntityToSchemaMapper[ReviewEntity, ReviewResponse]):
    def __init__(
            self,
            mapper: BookSchemaMapper
    ):
        self.mapper = mapper

    def from_entity_to_schema(self, entity: ReviewEntity) -> ReviewResponse:
        return ReviewResponse(
            id=entity.id,
            full_name=entity.full_name,
            review=entity.review,
            rating=entity.rating,
            book=self.mapper.from_entity_to_schema(entity=entity.book),
            created_at=entity.created_at
        )