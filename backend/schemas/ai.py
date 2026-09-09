from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ai.llm.schemas import CaseAnalysisResult


class AIAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    case_id: str
    analysis: CaseAnalysisResult
    model_name: str | None
    created_at: datetime | None = None


class PriorityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    case_id: str
    score: int
    priority_level: str
    reasons: list[str]
    created_at: datetime | None = None


class HybridPriorityResult(BaseModel):
    score: int
    priority_level: str
    reasons: list[str]


class HybridAnalysisResponse(BaseModel):
    """The available case AI results from one immutable hybrid run."""

    model_config = ConfigDict(from_attributes=True)

    analysis_id: int
    case_id: str
    llm_analysis: CaseAnalysisResult | None = None
    priority: HybridPriorityResult | None = None
    unavailable_components: list[str]
    created_at: datetime | None = None
