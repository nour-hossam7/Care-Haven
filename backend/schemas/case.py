from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CaseLevel = Literal["Low", "Medium", "High", "Critical"]
CaseStatus = Literal["Active", "Under Review", "Funded", "Completed"]


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    assistance_category: str = Field(min_length=1)
    people_affected: int = Field(ge=1)
    country: str = Field(min_length=1)
    governorate: str | None = None
    city: str | None = None
    latitude: Any | None = None
    longitude: Any | None = None
    severity: CaseLevel
    urgency: CaseLevel
    required_resources: str | None = None
    estimated_funding: Any | None = None


class CaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(default=None, min_length=1)
    assistance_category: str | None = Field(default=None, min_length=1)
    people_affected: int | None = Field(default=None, ge=1)
    country: str | None = Field(default=None, min_length=1)
    governorate: str | None = None
    city: str | None = None
    latitude: Any | None = None
    longitude: Any | None = None
    severity: CaseLevel | None = None
    urgency: CaseLevel | None = None
    required_resources: str | None = None
    estimated_funding: Any | None = None


class CaseStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: CaseStatus


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    description: str | None
    assistance_category: str | None
    people_affected: int | None
    country: str | None
    governorate: str | None
    city: str | None
    latitude: Any | None
    longitude: Any | None
    severity: str | None
    urgency: str | None
    required_resources: str | None
    estimated_funding: Any | None
    current_funding: Any | None
    submission_date: datetime | None
    status: str | None
    priority: str | None
    created_by: str | None


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    page: int
    page_size: int
    total: int
    pages: int
