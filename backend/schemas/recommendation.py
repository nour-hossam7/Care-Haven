from __future__ import annotations

from backend.schemas.case import CaseResponse


class RecommendationCase(CaseResponse):
    """One ranked case plus Person 2 recommendation metadata."""

    recommendation_rank: int
    recommendation_score: float
    recommendation_reasons: list[str]
    recommendation_breakdown: dict[str, float]