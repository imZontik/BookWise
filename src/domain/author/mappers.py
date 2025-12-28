from src.adapters.schemas.responses.author import AuthorResponse
from src.core.mappers import EntityToSchemaMapper
from src.domain.author.entities import AuthorEntity


class AuthorSchemaMapper(EntityToSchemaMapper[AuthorEntity, AuthorResponse]):
    def from_entity_to_schema(self, entity: AuthorEntity) -> AuthorResponse:
        return AuthorResponse(
            id=entity.id,
            name=entity.name,
            slug=entity.slug,
            bio=entity.bio,
            birth_date=entity.birth_date,
            death_date=entity.death_date,
            country=entity.country,
            photo_url=entity.photo_url
        )