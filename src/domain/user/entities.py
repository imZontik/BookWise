from dataclasses import dataclass
from uuid import UUID

from src.domain.user.enums import UserRole


@dataclass
class UserEntity:
    id: UUID
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole


@dataclass
class UserCreateEntity:
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole