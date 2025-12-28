from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import date


@dataclass
class AuthorEntity:
    id: UUID
    name: str
    slug: str
    bio: Optional[str]
    birth_date: Optional[date]
    death_date: Optional[date]
    country: Optional[str]
    photo_url: Optional[str]


@dataclass
class AuthorCreateEntity:
    name: str
    slug: str
    bio: Optional[str]
    birth_date: Optional[date]
    death_date: Optional[date]
    country: Optional[str]
