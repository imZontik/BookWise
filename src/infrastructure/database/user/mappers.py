from src.core.mappers import ModelToEntityMapper
from src.domain.user.entities import UserEntity
from src.infrastructure.database.user.models import UserModel


class UserModelMapper(ModelToEntityMapper[UserModel, UserEntity]):
    def from_model_to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            hashed_password=model.hashed_password,
            role=model.role
        )