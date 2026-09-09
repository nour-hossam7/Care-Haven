from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

if TYPE_CHECKING:
    from .ai_analysis import AIAnalysis
    from .case_image import CaseEvidence
    from .donation import Donation
    from .flag import Flag


class Case(Base):
    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(Text, primary_key=True)
    description: Mapped[str | None] = mapped_column(Text)
    assistance_category: Mapped[str | None] = mapped_column(Text)
    people_affected: Mapped[int | None] = mapped_column(Integer)
    country: Mapped[str | None] = mapped_column(Text)
    governorate: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[Any | None] = mapped_column(JSON)
    longitude: Mapped[Any | None] = mapped_column(JSON)
    severity: Mapped[str | None] = mapped_column(Text)
    urgency: Mapped[str | None] = mapped_column(Text)
    required_resources: Mapped[str | None] = mapped_column(Text)
    estimated_funding: Mapped[Any | None] = mapped_column(JSON)
    current_funding: Mapped[Any | None] = mapped_column(JSON)
    submission_date: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str | None] = mapped_column(Text)

    donations: Mapped[list[Donation]] = relationship(back_populates="case")
    evidence: Mapped[list[CaseEvidence]] = relationship(back_populates="case")
    analyses: Mapped[list[AIAnalysis]] = relationship(back_populates="case")
    flags: Mapped[list[Flag]] = relationship(back_populates="case")