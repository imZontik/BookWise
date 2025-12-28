from typing import Optional

from sqlalchemy import String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from src.core.database.models import SQLBaseModel


class AuthorModel(SQLBaseModel):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    death_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
