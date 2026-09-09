from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class UserRole(str, Enum):
    DONOR = "Donor"
    VOLUNTEER = "Volunteer"
    NGO = "NGO"
    BENEFICIARY = "Beneficiary"
    ADMIN = "Admin"


class User(Base):
    """Application authentication account, separate from the donors table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(
            UserRole,
            name="user_role",
            native_enum=False,
            values_callable=lambda roles: [role.value for role in roles],
        ),
        nullable=False,
        default=UserRole.DONOR,
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )