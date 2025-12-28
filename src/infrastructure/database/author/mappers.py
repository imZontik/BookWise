from src.core.mappers import ModelToEntityMapper
from src.domain.author.entities import AuthorEntity
from src.infrastructure.database.author.models import AuthorModel


class AuthorModelMapper(ModelToEntityMapper[AuthorModel, AuthorEntity]):
    def from_model_to_entity(self, model: AuthorModel) -> AuthorEntity:
        return AuthorEntity(
            id=model.id,
            name=model.name,
            slug=model.slug,
            bio=model.bio,
            birth_date=model.birth_date,
            death_date=model.death_date,
            country=model.country,
            photo_url=model.photo_url
        )