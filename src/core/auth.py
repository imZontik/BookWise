from uuid import UUID

from fastapi import Security, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt

from src.adapters.dependencies import get_user_repository
from src.core.config import settings
from src.domain.user.entities import UserEntity
from src.domain.user.protocols import UserRepositoryProtocol

bearer_scheme = HTTPBearer(auto_error=True)


async def get_user(
        creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
        repository: UserRepositoryProtocol = Depends(get_user_repository)
) -> UserEntity:
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.AUTH_SECRET_KEY,
            algorithms=[settings.AUTH_ALGORITHM],
            options={"verify_aud": False},
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Время токена истекло")
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен недействителен")

    user_id = UUID(payload.get("sub"))
    if not user_id:
        raise HTTPException(status_code=401, detail="Такого пользователя нет")

    user = await repository.find_by_id(model_id=user_id)

    if not user:
        raise HTTPException(status_code=401, detail="Такого пользователя нет")

    return user