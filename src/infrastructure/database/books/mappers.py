from src.core.mappers import ModelToEntityMapper
from src.domain.books.entities import BookEntity, FavouriteBookEntity
from src.infrastructure.database.books.models import BookModel, FavouriteBookModel


class BookModelMapper(ModelToEntityMapper[BookModel, BookEntity]):
    def from_model_to_entity(self, model: BookModel) -> BookEntity:
        return BookEntity(
            id=model.id,
            title=model.title,
            slug=model.slug,
            language=model.language,
            description=model.description,
            short_description=model.short_description,
            publish_year=model.publish_year,
            page_count=model.page_count,
            author_id=model.author_id,
            genre=model.genre
        )


class FavouriteBookModelMapper(ModelToEntityMapper[FavouriteBookModel, FavouriteBookEntity]):
    def __init__(
            self,
            mapper: BookModelMapper
    ):
        self.mapper = mapper

    def from_model_to_entity(self, model: FavouriteBookModel) -> FavouriteBookEntity:
        return FavouriteBookEntity(
            id=model.id,
            status=model.status,
            book=self.mapper.from_model_to_entity(model=model.book)
        )