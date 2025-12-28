import uuid
from unittest.mock import AsyncMock, create_autospec, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.schemas.requests.user import RegisterRequest, LogInRequest
from src.adapters.schemas.responses.user import TokenResponse
from src.application.usecases.user import RegisterUseCase, LogInUseCase
from src.core.uow import SQLAlchemyUoW
from src.domain.security.protocols import PasswordHasherProtocol, TokenServiceProtocol
from src.domain.user.entities import UserCreateEntity, UserEntity
from src.domain.user.enums import UserRole
from src.domain.user.exceptions import UserAlreadyExistException, InvalidCredentialsException
from src.domain.user.mappers import UserSchemaMapper
from src.domain.user.protocols import UserRepositoryProtocol


@pytest.mark.asyncio
class TestRegisterUseCase:
    async def test_execute_success(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.create = AsyncMock()

        created_entity = object()
        repository.create.return_value = created_entity

        mapper = create_autospec(UserSchemaMapper, instance=True)
        password_hasher = create_autospec(PasswordHasherProtocol, instance=True)
        password_hasher.hash.return_value = "hashed123"

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        uow = SQLAlchemyUoW(session=fake_session)

        use_case = RegisterUseCase(
            repository=repository,
            mapper=mapper,
            password_hasher=password_hasher,
            uow=uow
        )

        request = RegisterRequest(
            email="user@email.com",
            password="Test password",
            first_name="First name",
            last_name="Last name",
            is_admin=False
        )

        create_entity = UserCreateEntity(
            email=request.email,
            hashed_password="hashed123",
            first_name=request.first_name,
            last_name=request.last_name,
            role=UserRole.USER
        )

        response = {
            "id": uuid.uuid4(),
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name
        }

        mapper.from_entity_to_schema.return_value = response

        result = await use_case.execute(data=request)
        assert result == response

        password_hasher.hash.assert_called_once_with(password=request.password)
        mapper.from_entity_to_schema.assert_called_once_with(entity=created_entity)

        repository.create.assert_awaited_once_with(entity=create_entity)

        fake_session.commit.assert_awaited_once()
        fake_session.rollback.assert_not_awaited()

    async def test_execute_user_already_exist(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.create = AsyncMock(side_effect=UserAlreadyExistException())

        mapper = create_autospec(UserSchemaMapper, instance=True)
        password_hasher = create_autospec(PasswordHasherProtocol, instance=True)
        password_hasher.hash.return_value = "hashed123"

        fake_session = create_autospec(AsyncSession, instance=True)
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()

        uow = SQLAlchemyUoW(session=fake_session)

        use_case = RegisterUseCase(
            repository=repository,
            mapper=mapper,
            password_hasher=password_hasher,
            uow=uow
        )

        request = RegisterRequest(
            email="user@email.com",
            password="Test password",
            first_name="First name",
            last_name="Last name",
            is_admin=False
        )

        with pytest.raises(UserAlreadyExistException):
            await use_case.execute(data=request)

        password_hasher.hash.assert_called_once_with(password=request.password)

        fake_session.rollback.assert_awaited_once()
        fake_session.commit.assert_not_awaited()

        mapper.from_entity_to_schema.assert_not_called()


@pytest.mark.asyncio
class TestLogInUseCase:
    async def test_execute_success(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.find_by_email = AsyncMock()

        token_service = create_autospec(TokenServiceProtocol, instance=True)
        password_hasher = create_autospec(PasswordHasherProtocol, instance=True)

        user_entity = UserEntity(
            id=uuid.uuid4(),
            email="user@email.com",
            hashed_password="hashed123",
            first_name="First name",
            last_name="Last name",
            role=UserRole.USER
        )

        repository.find_by_email.return_value = user_entity
        token_service.create_access_token.return_value = "access_token"
        password_hasher.verify.return_value = True

        request = LogInRequest(
            email="user@email.com",
            password="password"
        )

        use_case = LogInUseCase(
            repository=repository,
            password_hasher=password_hasher,
            token_service=token_service
        )

        result = await use_case.execute(data=request)
        response = TokenResponse(access_token="access_token")

        assert result.access_token == response.access_token

        repository.find_by_email.assert_awaited_once_with(email=request.email)
        password_hasher.verify.assert_called_once_with(
            plain_password=request.password,
            hashed_password=user_entity.hashed_password
        )
        token_service.create_access_token.assert_called_once_with(
            data={"sub": str(user_entity.id)}
        )

    async def test_execute_find_by_email_returns_none(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.find_by_email = AsyncMock()

        token_service = create_autospec(TokenServiceProtocol, instance=True)
        password_hasher = create_autospec(PasswordHasherProtocol, instance=True)

        repository.find_by_email.return_value = None

        request = LogInRequest(
            email="user@email.com",
            password="password"
        )

        use_case = LogInUseCase(
            repository=repository,
            password_hasher=password_hasher,
            token_service=token_service
        )

        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(data=request)

        repository.find_by_email.assert_awaited_once_with(email=request.email)
        password_hasher.verify.assert_not_called()
        token_service.create_access_token.assert_not_called()

    async def test_execute_verify_returns_false(self):
        repository = create_autospec(UserRepositoryProtocol, instance=True)
        repository.find_by_email = AsyncMock()

        token_service = create_autospec(TokenServiceProtocol, instance=True)
        password_hasher = create_autospec(PasswordHasherProtocol, instance=True)

        user_entity = UserEntity(
            id=uuid.uuid4(),
            email="user@email.com",
            hashed_password="hashed123",
            first_name="First name",
            last_name="Last name",
            role=UserRole.USER
        )

        repository.find_by_email.return_value = user_entity
        password_hasher.verify.return_value = False

        request = LogInRequest(
            email="user@email.com",
            password="password"
        )

        use_case = LogInUseCase(
            repository=repository,
            password_hasher=password_hasher,
            token_service=token_service
        )

        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(data=request)

        repository.find_by_email.assert_awaited_once_with(email=request.email)
        password_hasher.verify.assert_called_once_with(
            plain_password=request.password,
            hashed_password=user_entity.hashed_password
        )
        token_service.create_access_token.assert_not_called()