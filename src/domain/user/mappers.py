from src.adapters.schemas.responses.user import UserResponse
from src.core.mappers import EntityToSchemaMapper
from src.domain.user.entities import UserEntity


class UserSchemaMapper(EntityToSchemaMapper[UserEntity, UserResponse]):
    def from_entity_to_schema(self, entity: UserEntity) -> UserResponse:
        return UserResponse(
            id=entity.id,
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role
        )