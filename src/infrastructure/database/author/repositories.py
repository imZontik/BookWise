from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.author.entities import AuthorCreateEntity, AuthorEntity
from src.domain.author.exceptions import AuthorAlreadyExistException
from src.domain.author.protocols import AuthorRepositoryProtocol
from src.infrastructure.database.author.mappers import AuthorModelMapper
from src.infrastructure.database.author.models import AuthorModel


class AuthorRepository(AuthorRepositoryProtocol):
    def __init__(
            self,
            session: AsyncSession,
            mapper: AuthorModelMapper
    ):
        self.session = session
        self.mapper = mapper
        self.model = AuthorModel

    async def create(self, entity: AuthorCreateEntity) -> AuthorEntity:
        model = self.model(
            name=entity.name,
            slug=entity.slug,
            bio=entity.bio,
            birth_date=entity.birth_date,
            death_date=entity.death_date,
            country=entity.country
        )

        self.session.add(model)

        try:
            async with self.session.begin_nested():
                await self.session.flush()
        except IntegrityError:
            raise AuthorAlreadyExistException()

        return self.mapper.from_model_to_entity(model)

    async def find_by_slug(self, slug: str) -> Optional[AuthorEntity]:
        statement = (
            select(self.model)
            .where(self.model.slug == slug)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.from_model_to_entity(model=model)

    async def find_by_id(self, model_id: UUID) -> Optional[AuthorEntity]:
        statement = (
            select(self.model)
            .where(self.model.id == model_id)
        )

        result = await self.session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self.mapper.from_model_to_entity(model=model)

    async def delete_by_id(self, model_id: UUID) -> bool:
        statement = (
            delete(self.model)
            .where(self.model.id == model_id)
        )

        result = await self.session.execute(statement)
        return result.rowcount > 0

    async def update_photo_url(self, model_id: UUID, photo_url: str) -> AuthorEntity:
        statement = (
            update(self.model)
            .where(self.model.id == model_id)
            .values(photo_url=photo_url)
            .returning(AuthorModel)
        )

        result = await self.session.execute(statement)
        return self.mapper.from_model_to_entity(result.scalar_one())

