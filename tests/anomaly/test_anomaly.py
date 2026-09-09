from __future__ import annotations

import json

import pytest

from ai.anomaly.detector import (
	analyze_dataset,
	detect_anomalies,
	detect_similar_cases,
)


def donation(donation_id: str, amount: str, donor_id: str = "DONOR-1", case_id: str = "CASE-1", day: str = "2026-01-01") -> dict[str, str]:
	return {"donation_id": donation_id, "amount": amount, "donor_id": donor_id, "case_id": case_id, "date": day}


def case(case_id: str, description: str = "A family needs food assistance.", **overrides: str) -> dict[str, str]:
	row = {
		"case_id": case_id,
		"description": description,
		"people_affected": "10",
		"estimated_funding": "1000",
		"current_funding": "200",
		"priority": "High",
		"status": "Active",
		"assistance_category": "Food",
	}
	row.update(overrides)
	return row


def test_obvious_donation_outlier_is_reviewable_and_not_fraud_label() -> None:
	records = [donation(f"DON-{index}", "10", case_id=f"CASE-{index}") for index in range(6)]
	records.append(donation("DON-OUTLIER", "10000", case_id="CASE-OUTLIER"))
	results = detect_anomalies(records, entity_type="donation", contamination=0.2, random_state=42)
	outlier = next(result for result in results if result["entity_id"] == "DON-OUTLIER")
	assert outlier["is_anomaly"]
	assert outlier["human_review_recommended"]
	assert any(signal["type"] in {"unusual_donation_amount", "numeric_activity_outlier"} for signal in outlier["signals"])
	assert "fraud" not in json.dumps(outlier).casefold()


def test_detection_is_deterministic_and_scores_are_bounded() -> None:
	records = [donation(f"DON-{index}", str(index + 1), case_id=f"CASE-{index}") for index in range(8)]
	first = detect_anomalies(records, entity_type="donation", random_state=42)
	second = detect_anomalies(records, entity_type="donation", random_state=42)
	assert first == second
	assert all(0.0 <= result["anomaly_score"] <= 1.0 for result in first)


def test_small_empty_and_malformed_inputs_are_safe() -> None:
	assert detect_anomalies([], entity_type="donation") == []
	one = detect_anomalies([donation("DON-1", "bad")], entity_type="donation")
	assert one[0]["is_anomaly"]
	assert one[0]["signals"][0]["type"] == "malformed_amount"
	cases = detect_anomalies([case("CASE-1", estimated_funding="bad")], entity_type="case")
	assert cases[0]["signals"][0]["type"] == "malformed_funding"


def test_invalid_configuration_is_explicit() -> None:
	with pytest.raises(ValueError):
		detect_anomalies([donation("DON-1", "1")], contamination=0)
	with pytest.raises(ValueError):
		detect_anomalies([donation("DON-1", "1")], n_estimators=0)
	with pytest.raises(ValueError):
		detect_anomalies([donation("DON-1", "1")], entity_type="donor")


def test_case_funding_conflict_is_flagged() -> None:
	result = detect_anomalies([case("CASE-1", current_funding="2000")], entity_type="case")[0]
	assert result["risk_level"] == "HIGH"
	assert result["signals"][0]["type"] == "inconsistent_funding"
	assert result["human_review_recommended"]


def test_exact_and_high_similarity_case_descriptions() -> None:
	cases = [
		case("CASE-1", "Families need clean water after flooding.") ,
		case("CASE-2", "  Families need clean water after flooding. "),
		case("CASE-3", "Families need clean water following flooding."),
		case("CASE-4", "A school needs books and desks."),
	]
	pairs = detect_similar_cases(cases, threshold=0.65)
	assert pairs[0]["exact"]
	assert pairs[0]["similarity_score"] == 1.0
	assert {pairs[0]["case_id"], pairs[0]["matched_case_id"]} == {"CASE-1", "CASE-2"}
	assert all(pair["case_id"] != pair["matched_case_id"] for pair in pairs)


def test_similarity_threshold_and_missing_descriptions() -> None:
	cases = [case("CASE-1", "short"), case("CASE-2", "different text"), case("CASE-3", "")]
	assert detect_similar_cases(cases, threshold=0.99) == []
	with pytest.raises(ValueError):
		detect_similar_cases(cases, threshold=1.1)


def test_dataset_report_attaches_similarity_signals_and_is_json_safe() -> None:
	report = analyze_dataset(
		[case("CASE-1", "Same description."), case("CASE-2", "Same description.")],
		[donation("DON-1", "10")],
		[{"donor_id": "DONOR-1"}],
	)
	assert report["similar_case_pairs"]
	assert any(result["signals"] for result in report["cases"])
	json.dumps(report)


def test_no_duplicate_anomaly_records() -> None:
	results = detect_anomalies([donation("DON-1", "10"), donation("DON-2", "20")], entity_type="donation")
	ids = [result["entity_id"] for result in results]
	assert len(ids) == len(set(ids))
