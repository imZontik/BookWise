from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy.orm import mapped_column, Mapped

from src.core.database.database import Base


class SQLBaseModel(Base):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )