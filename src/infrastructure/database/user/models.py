from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.models import SQLBaseModel
from src.domain.user.enums import UserRole


class UserModel(SQLBaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.USER,
        nullable=False
    )

    reviews = relationship("ReviewModel", back_populates="user")