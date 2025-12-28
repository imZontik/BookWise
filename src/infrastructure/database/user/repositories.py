from typing import Optional

from sqlalchemy import select, UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.entities import UserCreateEntity, UserEntity
from src.domain.user.exceptions import UserAlreadyExistException
from src.domain.user.protocols import UserRepositoryProtocol
from src.infrastructure.database.user.mappers import UserModelMapper
from src.infrastructure.database.user.models import UserModel


class UserRepository(UserRepositoryProtocol):
    def __init__(
            self,
            session: AsyncSession,
            mapper: UserModelMapper
    ):
        self.session = session
        self.model = UserModel
        self.mapper = mapper

    async def create(self, entity: UserCreateEntity) -> UserEntity:
        model = self.model(
            email=entity.email,
            hashed_password=entity.hashed_password,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role
        )

        self.session.add(model)

        try:
            async with self.session.begin_nested():
                await self.session.flush()
        except IntegrityError:
            raise UserAlreadyExistException()

        return self.mapper.from_model_to_entity(model=model)

    async def find_by_id(self, model_id: UUID) -> Optional[UserEntity]:
        statement = (
            select(self.model)
            .where(self.model.id == model_id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.from_model_to_entity(model=model)

    async def find_by_email(self, email: str) -> Optional[UserEntity]:
        statement = (
            select(self.model)
            .where(self.model.email == email)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.from_model_to_entity(model=model)