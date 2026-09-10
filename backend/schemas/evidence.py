from __future__ import annotations

from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict


VerificationStatus = Literal["unreviewed", "approved", "rejected"]


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evidence_id: str
    case_id: str | None
    evidence_type: str | None
    file_path: str | None
    source_type: str | None
    uploaded_at: datetime | None
    description: str | None
    verification_status: str | None


class CaseEvidenceResponse(EvidenceResponse):
    file_path: None = None
    image_url: str | None = None


class EvidenceVerificationUpdate(BaseModel):
    verification_status: VerificationStatus


class EvidenceListResponse(BaseModel):
    items: list[EvidenceResponse]
    page: int
    page_size: int
    total: int
    pages: int
