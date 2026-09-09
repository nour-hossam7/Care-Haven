from __future__ import annotations

from typing import Any

import pytest

from ai.recommendation.matcher import match_donor_to_cases
from ai.recommendation.ranker import DEFAULT_WEIGHTS, rank_candidates, recommend_cases


def case(case_id: str, **overrides: Any) -> dict[str, Any]:
	row: dict[str, Any] = {
		"case_id": case_id,
		"description": "A household needs humanitarian assistance.",
		"assistance_category": "Food",
		"people_affected": "10",
		"country": "Egypt",
		"governorate": "Cairo",
		"city": "Cairo",
		"urgency": "High",
		"priority": "High",
		"estimated_funding": "1000",
		"current_funding": "200",
		"status": "Active",
	}
	row.update(overrides)
	return row


def donor(**overrides: Any) -> dict[str, Any]:
	row: dict[str, Any] = {
		"donor_id": "DONOR-001",
		"preferred_category": "Food",
		"preferred_location": "Egypt - Cairo",
		"urgency_preference": "High",
		"budget": "2000",
	}
	row.update(overrides)
	return row


def test_category_location_and_priority_matching_are_explainable() -> None:
	candidate = match_donor_to_cases(donor(), [case("CASE-001")])[0]
	recommendation = rank_candidates(donor(), [candidate], top_n=1)[0]
	assert recommendation.score == pytest.approx(0.899)
	assert recommendation.breakdown["category"] == 1.0
	assert recommendation.breakdown["location"] == 1.0
	assert recommendation.breakdown["priority"] == pytest.approx(0.85)
	assert "Matches preferred assistance category" in recommendation.reasons
	assert "Matches preferred location" in recommendation.reasons


def test_funding_gap_and_open_case_filtering() -> None:
	cases = [
		case("CASE-OPEN", estimated_funding="1000", current_funding="100"),
		case("CASE-FULL", estimated_funding="1000", current_funding="1000"),
		case("CASE-CLOSED", status="Completed"),
	]
	candidates = match_donor_to_cases(donor(), cases)
	assert [candidate.case_id for candidate in candidates] == ["CASE-OPEN"]
	recommendation = rank_candidates(donor(), candidates)[0]
	assert recommendation.breakdown["funding_need"] > 0.5
	assert "remaining funding need" in " ".join(recommendation.reasons)


def test_missing_preferences_are_neutral_and_missing_case_fields_do_not_crash() -> None:
	candidates = match_donor_to_cases(
		donor(preferred_category="", preferred_location="", urgency_preference=""),
		[case("CASE-001", assistance_category=None, priority=None, urgency=None)],
	)
	assert len(candidates) == 1
	recommendation = rank_candidates(donor(preferred_category="", preferred_location="", urgency_preference=""), candidates)[0]
	assert 0.0 <= recommendation.score <= 1.0


def test_unknown_categories_are_safe() -> None:
	candidates = match_donor_to_cases(donor(preferred_category="Not A Category"), [case("CASE-001", assistance_category="New Aid")])
	assert len(candidates) == 1
	assert rank_candidates(donor(preferred_category="Not A Category"), candidates)[0].score >= 0.0


def test_donor_history_uses_joined_case_category_and_location() -> None:
	cases = [case("CASE-001"), case("CASE-002", assistance_category="Medical Aid", governorate="Giza")]
	donations = [{"donor_id": "DONOR-001", "case_id": "CASE-001", "amount": "50", "date": "2026-01-01"}]
	candidates = match_donor_to_cases(donor(), cases, donations)
	by_id = {candidate.case_id: candidate for candidate in candidates}
	assert by_id["CASE-001"].history_match == 1.0
	assert by_id["CASE-002"].history_match == 0.0
	recommendation = rank_candidates(donor(), [by_id["CASE-001"]])[0]
	assert "previous giving history" in " ".join(recommendation.reasons)


def test_no_candidates_and_top_n_contract() -> None:
	result = recommend_cases("DONOR-001", [case("CASE-001", status="Completed")], [donor()], top_n=5)
	assert result["candidate_count"] == 0
	assert result["recommendations"] == []
	cases = [case(f"CASE-{index:03d}") for index in range(4)]
	result = recommend_cases("DONOR-001", cases, [donor()], top_n=2)
	assert len(result["recommendations"]) == 2
	assert [item["rank"] for item in result["recommendations"]] == [1, 2]


def test_duplicate_cases_are_removed_and_ties_are_deterministic() -> None:
	cases = [case("CASE-002"), case("CASE-001"), case("CASE-002")]
	first = match_donor_to_cases(donor(), cases)
	second = match_donor_to_cases(donor(), cases)
	assert [candidate.case_id for candidate in first] == ["CASE-001", "CASE-002"]
	assert [item.case_id for item in rank_candidates(donor(), first)] == ["CASE-001", "CASE-002"]
	assert [item.case_id for item in rank_candidates(donor(), second)] == ["CASE-001", "CASE-002"]


def test_scores_are_normalized_and_weights_are_configurable() -> None:
	candidates = match_donor_to_cases(donor(), [case("CASE-001")])
	recommendation = rank_candidates(donor(), candidates, weights=DEFAULT_WEIGHTS)[0]
	assert 0.0 <= recommendation.score <= 1.0
	with pytest.raises(ValueError):
		rank_candidates(donor(), candidates, weights={"category": 1.0}, top_n=1)


def test_invalid_parameters_and_unknown_donor_are_explicit() -> None:
	with pytest.raises(ValueError):
		match_donor_to_cases(donor(), [case("CASE-001")], candidate_limit=0)
	with pytest.raises(ValueError):
		recommend_cases("MISSING", [case("CASE-001")], [donor()])
