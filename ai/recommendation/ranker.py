"""Explainable weighted ranking for CareHaven recommendation candidates."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .matcher import CandidateCase, LEVELS, match_donor_to_cases

DEFAULT_WEIGHTS: dict[str, float] = {
	"category": 0.30,
	"location": 0.25,
	"priority": 0.20,
	"funding_need": 0.15,
	"donor_behavior": 0.10,
}
ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Recommendation:
	"""One ranked recommendation with normalized score and reasons."""

	case_id: str
	rank: int
	score: float
	reasons: tuple[str, ...]
	breakdown: dict[str, float]
	case: dict[str, Any]

	def as_dict(self) -> dict[str, Any]:
		return {
			"case_id": self.case_id,
			"rank": self.rank,
			"score": self.score,
			"reasons": list(self.reasons),
			"breakdown": dict(self.breakdown),
			"case": dict(self.case),
		}


def _validate_weights(weights: Mapping[str, float] | None) -> dict[str, float]:
	selected = dict(DEFAULT_WEIGHTS if weights is None else weights)
	if set(selected) != set(DEFAULT_WEIGHTS):
		raise ValueError(f"weights must contain exactly: {', '.join(DEFAULT_WEIGHTS)}")
	if any(value < 0 for value in selected.values()):
		raise ValueError("weights must be non-negative")
	total = sum(selected.values())
	if total <= 0:
		raise ValueError("weights must have a positive total")
	return {key: value / total for key, value in selected.items()}


def _funding_score(candidate: CandidateCase, donor: Mapping[str, Any]) -> float:
	gap_ratio = min(1.0, candidate.funding_gap / candidate.funding_goal) if candidate.funding_goal else 0.0
	budget = float(donor.get("budget", 0) or 0)
	affordability = min(1.0, budget / candidate.funding_gap) if candidate.funding_gap and budget > 0 else 0.0
	return 0.7 * gap_ratio + 0.3 * affordability


def _score_candidate(candidate: CandidateCase, donor: Mapping[str, Any], weights: Mapping[str, float]) -> tuple[float, dict[str, float]]:
	priority_preference = candidate.urgency_match
	priority_component = 0.6 * candidate.priority_value + 0.4 * priority_preference
	breakdown = {
		"category": candidate.category_match,
		"location": candidate.location_match,
		"priority": priority_component,
		"funding_need": _funding_score(candidate, donor),
		"donor_behavior": candidate.history_match,
	}
	score = sum(breakdown[key] * weights[key] for key in breakdown)
	return round(min(1.0, max(0.0, score)), 6), breakdown


def _reasons(candidate: CandidateCase, donor: Mapping[str, Any], breakdown: Mapping[str, float]) -> tuple[str, ...]:
	reasons: list[str] = []
	if candidate.category_match == 1.0:
		reasons.append("Matches preferred assistance category")
	if candidate.location_match == 1.0:
		reasons.append("Matches preferred location")
	elif candidate.location_match == 0.5 and donor.get("preferred_location"):
		reasons.append("Shares part of the preferred location")
	priority = str(candidate.case.get("priority", "")).strip().casefold()
	if priority == "critical":
		reasons.append("Critical humanitarian priority")
	elif priority == "high":
		reasons.append("High humanitarian priority")
	if candidate.funding_gap > 0 and breakdown["funding_need"] >= 0.5:
		reasons.append("Significant remaining funding need")
	if candidate.history_match == 1.0:
		reasons.append("Aligns with the donor's previous giving history")
	if not reasons:
		reasons.append("Eligible open case with a remaining funding need")
	return tuple(reasons)


def rank_candidates(
	donor: Mapping[str, Any],
	candidates: Iterable[CandidateCase],
	*,
	weights: Mapping[str, float] | None = None,
	top_n: int = 5,
) -> list[Recommendation]:
	"""Score and deterministically rank already-generated candidates."""

	if top_n <= 0:
		raise ValueError("top_n must be greater than zero")
	normalized_weights = _validate_weights(weights)
	scored: list[tuple[CandidateCase, float, dict[str, float]]] = []
	for candidate in candidates:
		score, breakdown = _score_candidate(candidate, donor, normalized_weights)
		scored.append((candidate, score, breakdown))
	scored.sort(
		key=lambda item: (
			-item[1],
			-LEVELS.get(str(item[0].case.get("priority", "")).strip().casefold(), 0),
			item[0].case_id,
		)
	)
	recommendations: list[Recommendation] = []
	for rank, (candidate, score, breakdown) in enumerate(scored[:top_n], start=1):
		recommendations.append(
			Recommendation(
				case_id=candidate.case_id,
				rank=rank,
				score=score,
				reasons=_reasons(candidate, donor, breakdown),
				breakdown=breakdown,
				case=dict(candidate.case),
			)
		)
	return recommendations


def recommend_cases(
	donor_id: str,
	cases: Iterable[Mapping[str, Any]],
	donors: Iterable[Mapping[str, Any]],
	donations: Iterable[Mapping[str, Any]] | None = None,
	*,
	top_n: int = 5,
	weights: Mapping[str, float] | None = None,
) -> dict[str, Any]:
	"""Return a stable recommendation response for one donor."""

	if not donor_id or not donor_id.strip():
		raise ValueError("donor_id must not be empty")
	donor = next((dict(row) for row in donors if str(row.get("donor_id", "")).strip() == donor_id.strip()), None)
	if donor is None:
		raise ValueError(f"Unknown donor_id: {donor_id}")
	candidates = match_donor_to_cases(donor, cases, donations)
	ranked = rank_candidates(donor, candidates, weights=weights, top_n=top_n)
	return {
		"donor_id": donor_id.strip(),
		"candidate_count": len(candidates),
		"recommendations": [recommendation.as_dict() for recommendation in ranked],
	}


def load_csv_records(path: str | Path) -> list[dict[str, str]]:
	"""Load records for demos only; ranking remains independent of CSV files."""

	with Path(path).open(encoding="utf-8", newline="") as handle:
		return list(csv.DictReader(handle))


def load_default_data() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
	"""Load the repository's existing cases, donors, and donations for demos."""

	return (
		load_csv_records(ROOT / "data/raw/cases/cases.csv"),
		load_csv_records(ROOT / "data/raw/donors/donors.csv"),
		load_csv_records(ROOT / "data/raw/donations/donations.csv"),
	)
