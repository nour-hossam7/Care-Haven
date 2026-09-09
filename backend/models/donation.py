from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from .case import Case
    from .donor import Donor
    from .user import User


class Donation(Base):
    __tablename__ = "donations"

    donation_id: Mapped[str] = mapped_column(Text, primary_key=True)

    donor_id: Mapped[str | None] = mapped_column(
        ForeignKey("donors.donor_id"),
        nullable=True,
    )

    case_id: Mapped[str | None] = mapped_column(
        ForeignKey("cases.case_id"),
        nullable=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )

    amount: Mapped[Any | None] = mapped_column(JSON)
    date: Mapped[datetime | None] = mapped_column(DateTime)

    donor: Mapped[Donor | None] = relationship(
        back_populates="donations",
    )

    case: Mapped[Case | None] = relationship(
        back_populates="donations",
    )

    user: Mapped[User | None] = relationship(
        back_populates="donations",
    )