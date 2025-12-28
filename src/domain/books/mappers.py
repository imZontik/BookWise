from src.adapters.schemas.responses.books import BookResponse, FavouriteBookResponse
from src.core.mappers import EntityToSchemaMapper
from src.domain.books.entities import BookEntity, FavouriteBookEntity


class BookSchemaMapper(EntityToSchemaMapper[BookEntity, BookResponse]):
    def from_entity_to_schema(self, entity: BookEntity) -> BookResponse:
        return BookResponse(
            id=entity.id,
            title=entity.title,
            slug=entity.slug,
            language=entity.language,
            description=entity.description,
            short_description=entity.short_description,
            publish_year=entity.publish_year,
            page_count=entity.page_count,
            author_id=entity.author_id,
            genre=entity.genre
        )


class FavouriteBookSchemaMapper(EntityToSchemaMapper[FavouriteBookEntity, FavouriteBookResponse]):
    def __init__(
            self,
            mapper: BookSchemaMapper
    ):
        self.mapper = mapper

    def from_entity_to_schema(self, entity: FavouriteBookEntity) -> FavouriteBookResponse:
        return FavouriteBookResponse(
            id=entity.id,
            status=entity.status,
            book=self.mapper.from_entity_to_schema(entity=entity.book)
        )