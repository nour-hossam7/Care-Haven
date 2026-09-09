from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from .donation import Donation


class Donor(Base):
    """Existing anonymous donor preference record, not an authentication user."""

    __tablename__ = "donors"

    donor_id: Mapped[str] = mapped_column(Text, primary_key=True)
    preferred_category: Mapped[str | None] = mapped_column(Text)
    budget: Mapped[Any | None] = mapped_column(JSON)
    preferred_location: Mapped[str | None] = mapped_column(Text)
    urgency_preference: Mapped[str | None] = mapped_column(Text)
    previous_donations: Mapped[int | None] = mapped_column(Integer)

    donations: Mapped[list[Donation]] = relationship(back_populates="donor")