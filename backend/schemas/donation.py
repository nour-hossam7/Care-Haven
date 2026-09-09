from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DonationCreate(BaseModel):
    """Client-controlled inputs for an application donation."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)


class DonationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    donation_id: str
    case_id: str | None
    user_id: str | None
    donor_id: str | None
    amount: Any | None
    date: datetime | None


class DonationListResponse(BaseModel):
    items: list[DonationResponse]
    page: int
    page_size: int
    total: int
    pages: int
