from datetime import datetime

from jose import jwt
from asyncpg.pgproto.pgproto import timedelta
from passlib.context import CryptContext

from src.core.config import settings
from src.domain.security.protocols import (
    PasswordHasherProtocol,
    TokenServiceProtocol
)

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto"
)


class PasswordHasher(PasswordHasherProtocol):
    def hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class TokenService(TokenServiceProtocol):
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire_time = datetime.now() + timedelta(minutes=120)
        to_encode.update({
            "exp": expire_time
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.AUTH_SECRET_KEY,
            settings.AUTH_ALGORITHM
        )

        return encoded_jwt