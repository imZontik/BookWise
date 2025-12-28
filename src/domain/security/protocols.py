from typing import Protocol


class PasswordHasherProtocol(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


class TokenServiceProtocol(Protocol):
    def create_access_token(self, data: dict) -> str: ...