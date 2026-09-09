from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from .case import Case
    from .donation import Donation


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """Application authentication account, separate from the donors table."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(
            UserRole,
            name="user_role",
            native_enum=False,
            values_callable=lambda roles: [role.value for role in roles],
        ),
        nullable=False,
        default=UserRole.USER,
        server_default="user",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    cases: Mapped[list[Case]] = relationship(
        back_populates="creator",
    )

    donations: Mapped[list[Donation]] = relationship(
        back_populates="user",
    )