from __future__ import annotations

from dataclasses import dataclass
from numbers import Real


LEVEL_SCORES = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
EMERGENCY_CATEGORIES = {"Medical Aid", "Emergency Housing"}


class PriorityCalculationError(ValueError):
    """Raised when the established priority rule cannot score a case."""


@dataclass(frozen=True)
class PriorityResult:
    score: int
    priority_level: str
    reasons: list[str]


def _numeric(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise PriorityCalculationError(f"{field} must be a number")
    return float(value)


def calculate_priority(
    *,
    severity: str | None,
    urgency: str | None,
    people_affected: int | None,
    estimated_funding: object,
    current_funding: object,
    assistance_category: str | None,
) -> PriorityResult:
    """Apply the project's existing synthetic-data priority formula unchanged."""

    if severity not in LEVEL_SCORES or urgency not in LEVEL_SCORES:
        raise PriorityCalculationError("severity and urgency must be valid case levels")
    if isinstance(people_affected, bool) or not isinstance(people_affected, int) or people_affected < 1:
        raise PriorityCalculationError("people_affected must be a positive integer")
    estimated = _numeric(estimated_funding, "estimated_funding")
    current = _numeric(current_funding, "current_funding")
    if estimated <= 0 or current < 0:
        raise PriorityCalculationError("funding values must be non-negative and estimated_funding must be positive")

    people_score = 1 if people_affected < 10 else 2 if people_affected < 50 else 3
    funding_gap_ratio = max(0.0, 1 - (current / estimated))
    gap_score = 0 if funding_gap_ratio < 0.10 else 1 if funding_gap_ratio < 0.40 else 2 if funding_gap_ratio < 0.75 else 3
    emergency_score = 1 if assistance_category in EMERGENCY_CATEGORIES else 0
    score = LEVEL_SCORES[severity] + LEVEL_SCORES[urgency] + people_score + gap_score + emergency_score
    priority_level = "Critical" if score >= 13 else "High" if score >= 10 else "Medium" if score >= 7 else "Low"
    reasons = [
        f"Severity: {severity}",
        f"Urgency: {urgency}",
        f"People affected band: {people_score}",
        f"Funding gap band: {gap_score}",
    ]
    if emergency_score:
        reasons.append("Emergency assistance category")
    return PriorityResult(score=score, priority_level=priority_level, reasons=reasons)
