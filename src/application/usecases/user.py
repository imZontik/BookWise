from src.adapters.schemas.requests.user import RegisterRequest, LogInRequest
from src.adapters.schemas.responses.user import UserResponse, TokenResponse
from src.core.uow import SQLAlchemyUoW
from src.domain.security.protocols import PasswordHasherProtocol, TokenServiceProtocol
from src.domain.user.entities import UserCreateEntity
from src.domain.user.enums import UserRole
from src.domain.user.exceptions import InvalidCredentialsException
from src.domain.user.mappers import UserSchemaMapper
from src.domain.user.protocols import RegisterUseCaseProtocol, LogInUseCaseProtocol, UserRepositoryProtocol


class RegisterUseCase(RegisterUseCaseProtocol):
    def __init__(
            self,
            repository: UserRepositoryProtocol,
            mapper: UserSchemaMapper,
            password_hasher: PasswordHasherProtocol,
            uow: SQLAlchemyUoW
    ):
        self.repository = repository
        self.mapper = mapper
        self.password_hasher = password_hasher
        self.uow = uow

    async def execute(self, data: RegisterRequest) -> UserResponse:
        hashed_password = self.password_hasher.hash(password=data.password)

        create_entity = UserCreateEntity(
            email=data.email,
            hashed_password=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
            role=UserRole.ADMIN if data.is_admin else UserRole.USER
        )

        async with self.uow:
            result = await self.repository.create(entity=create_entity)
            return self.mapper.from_entity_to_schema(entity=result)


class LogInUseCase(LogInUseCaseProtocol):
    def __init__(
            self,
            repository: UserRepositoryProtocol,
            password_hasher: PasswordHasherProtocol,
            token_service: TokenServiceProtocol
    ):
        self.repository = repository
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def execute(self, data: LogInRequest) -> TokenResponse:
        result = await self.repository.find_by_email(email=data.email)

        if result is None:
            raise InvalidCredentialsException()

        if not self.password_hasher.verify(
                plain_password=data.password,
                hashed_password=result.hashed_password
        ):
            raise InvalidCredentialsException()

        data = {"sub": str(result.id)}
        access_token = self.token_service.create_access_token(data=data)

        return TokenResponse(access_token=access_token)



