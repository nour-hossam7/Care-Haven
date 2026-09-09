"""Candidate generation for transparent donor-to-case recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

ACTIVE_STATUSES = frozenset({"active", "under review"})
LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _text(value: Any) -> str:
	return str(value).strip().casefold() if value is not None else ""


def _number(value: Any, default: float | None = None) -> float | None:
	try:
		return float(value)
	except (TypeError, ValueError):
		return default


def case_location(case: Mapping[str, Any]) -> str:
	"""Return the normalized country/governorate location used by donors."""

	country = _text(case.get("country"))
	governorate = _text(case.get("governorate"))
	return f"{country} - {governorate}" if country and governorate else country or governorate


def location_similarity(preferred: Any, case: Mapping[str, Any]) -> float:
	"""Return exact-location, component-location, or neutral similarity."""

	wanted = _text(preferred)
	actual = case_location(case)
	if not wanted or not actual:
		return 0.5
	if wanted == actual:
		return 1.0
	wanted_parts = {_text(part) for part in str(preferred).split("-") if _text(part)}
	actual_parts = {_text(case.get("country")), _text(case.get("governorate")), _text(case.get("city"))}
	return 0.5 if wanted_parts & actual_parts else 0.0


def _history_by_donor(
	donations: Iterable[Mapping[str, Any]], cases_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, set[str]]]:
	history: dict[str, dict[str, set[str]]] = {}
	for donation in donations:
		donor_id = str(donation.get("donor_id", "")).strip()
		case = cases_by_id.get(str(donation.get("case_id", "")).strip())
		if not donor_id or case is None:
			continue
		record = history.setdefault(donor_id, {"categories": set(), "locations": set()})
		category = _text(case.get("assistance_category"))
		location = case_location(case)
		if category:
			record["categories"].add(category)
		if location:
			record["locations"].add(location)
	return history


@dataclass(frozen=True)
class CandidateCase:
	"""An eligible case plus matching signals for the ranking stage."""

	case: dict[str, Any]
	category_match: float
	location_match: float
	urgency_match: float
	priority_value: float
	funding_gap: float
	funding_goal: float
	history_match: float
	history_categories: frozenset[str] = field(default_factory=frozenset)
	history_locations: frozenset[str] = field(default_factory=frozenset)

	@property
	def case_id(self) -> str:
		return str(self.case["case_id"])


def is_eligible_case(case: Mapping[str, Any]) -> bool:
	"""Return whether a case is open and has a remaining funding need."""

	if not _text(case.get("case_id")) or _text(case.get("status")) not in ACTIVE_STATUSES:
		return False
	goal = _number(case.get("estimated_funding"))
	current = _number(case.get("current_funding"))
	return goal is not None and goal > 0 and current is not None and current < goal


def match_donor_to_cases(
	donor: Mapping[str, Any],
	cases: Iterable[Mapping[str, Any]],
	donations: Iterable[Mapping[str, Any]] | None = None,
	*,
	candidate_limit: int | None = None,
) -> list[CandidateCase]:
	"""Generate eligible candidate records without performing final ranking.

	Missing donor preferences are neutral and therefore do not exclude cases.
	Donation history is optional and only derives category/location signals by
	joining the supplied donations to the supplied cases.
	"""

	if candidate_limit is not None and candidate_limit <= 0:
		raise ValueError("candidate_limit must be greater than zero")
	donor_id = str(donor.get("donor_id", "")).strip()
	case_rows = [dict(case) for case in cases]
	cases_by_id = {str(case.get("case_id", "")).strip(): case for case in case_rows if case.get("case_id")}
	history = _history_by_donor(donations or [], cases_by_id) if donor_id else {}
	donor_history = history.get(donor_id, {"categories": set(), "locations": set()})
	candidates: list[CandidateCase] = []
	seen: set[str] = set()
	preferred_category = _text(donor.get("preferred_category"))
	preferred_urgency = _text(donor.get("urgency_preference"))
	budget = _number(donor.get("budget"), 0.0) or 0.0
	for case in case_rows:
		case_id = str(case.get("case_id", "")).strip()
		if case_id in seen or not is_eligible_case(case):
			continue
		seen.add(case_id)
		category = _text(case.get("assistance_category"))
		category_match = 0.5 if not preferred_category else float(category == preferred_category)
		location_match = location_similarity(donor.get("preferred_location"), case)
		case_urgency = _text(case.get("urgency"))
		urgency_match = 0.5 if not preferred_urgency else (1.0 if case_urgency == preferred_urgency else 0.0)
		priority_label = _text(case.get("priority")) or case_urgency
		priority_value = LEVELS.get(priority_label, 0) / 4.0
		goal = _number(case.get("estimated_funding"), 0.0) or 0.0
		current = _number(case.get("current_funding"), 0.0) or 0.0
		gap = max(goal - current, 0.0)
		category_history = frozenset(donor_history["categories"])
		location_history = frozenset(donor_history["locations"])
		if not category_history and not location_history:
			history_match = 0.5
		else:
			history_match = max(
				float(category in category_history) if category else 0.0,
				float(case_location(case) in location_history) if case_location(case) else 0.0,
			)
		candidates.append(
			CandidateCase(
				case=case,
				category_match=category_match,
				location_match=location_match,
				urgency_match=urgency_match,
				priority_value=priority_value,
				funding_gap=gap,
				funding_goal=goal,
				history_match=history_match,
				history_categories=category_history,
				history_locations=location_history,
			)
		)
	candidates.sort(key=lambda candidate: candidate.case_id)
	if candidate_limit is not None:
		return candidates[:candidate_limit]
	return candidates
