"""Deterministic, explainable anomaly signals for CareHaven records.

The detector produces review signals only. It never labels a person, donor, or
case as fraudulent and does not mutate source records.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping, Sequence

DEFAULT_CONTAMINATION = 0.05
DEFAULT_ESTIMATORS = 100
DEFAULT_RANDOM_STATE = 42
DEFAULT_SIMILARITY_THRESHOLD = 0.85
RISK_THRESHOLDS = {"medium": 0.45, "high": 0.75}


class AnomalyConfigurationError(ValueError):
	"""Raised for invalid detector configuration."""


@dataclass(frozen=True)
class SimilarityPair:
	"""A pair of case descriptions with deterministic similarity evidence."""

	case_id: str
	matched_case_id: str
	similarity_score: float
	exact: bool
	reason: str

	def as_dict(self) -> dict[str, Any]:
		return {
			"case_id": self.case_id,
			"matched_case_id": self.matched_case_id,
			"similarity_score": self.similarity_score,
			"exact": self.exact,
			"reason": self.reason,
		}


def _text(value: Any) -> str:
	return str(value).strip() if value is not None else ""


def _number(value: Any) -> float | None:
	try:
		result = float(value)
		return result if math.isfinite(result) else None
	except (TypeError, ValueError):
		return None


def _date(value: Any) -> date | None:
	try:
		return date.fromisoformat(_text(value))
	except ValueError:
		return None


def normalize_description(value: Any) -> str:
	"""Normalize case text for exact duplicate detection."""

	return re.sub(r"\s+", " ", _text(value).casefold()).strip()


def _result(
	entity_id: str,
	entity_type: str,
	score: float,
	signals: list[dict[str, Any]],
) -> dict[str, Any]:
	score = round(min(1.0, max(0.0, score)), 6)
	risk_level = "HIGH" if score >= RISK_THRESHOLDS["high"] else "MEDIUM" if score >= RISK_THRESHOLDS["medium"] else "LOW"
	is_anomaly = bool(signals) or score >= RISK_THRESHOLDS["medium"]
	if is_anomaly and not signals:
		signals = [{
			"type": "isolation_forest",
			"severity": risk_level,
			"message": "The observed numeric pattern differs from the reference records.",
		}]
	return {
		"entity_id": entity_id,
		"entity_type": entity_type,
		"anomaly_score": score,
		"risk_level": risk_level,
		"is_anomaly": is_anomaly,
		"signals": signals,
		"human_review_recommended": is_anomaly,
	}


def _signal(signal_type: str, severity: str, message: str, **extra: Any) -> dict[str, Any]:
	signal: dict[str, Any] = {"type": signal_type, "severity": severity, "message": message}
	signal.update(extra)
	return signal


def _validate_configuration(contamination: float, n_estimators: int) -> None:
	if not 0 < contamination < 0.5:
		raise AnomalyConfigurationError("contamination must be greater than 0 and less than 0.5")
	if n_estimators <= 0:
		raise AnomalyConfigurationError("n_estimators must be greater than zero")


def _isolation_scores(features: Sequence[Sequence[float]], contamination: float, n_estimators: int, random_state: int) -> tuple[list[float], list[bool]]:
	"""Return normalized anomaly scores and IsolationForest flags safely."""

	if len(features) < 2:
		return [0.0] * len(features), [False] * len(features)
	try:
		from sklearn.ensemble import IsolationForest
	except ImportError as exc:
		raise RuntimeError("scikit-learn is required for numerical anomaly detection") from exc
	model = IsolationForest(
		contamination=min(contamination, max(1 / len(features), 0.01)),
		n_estimators=n_estimators,
		random_state=random_state,
	)
	model.fit(features)
	raw = [-float(value) for value in model.decision_function(features)]
	lower, upper = min(raw), max(raw)
	if upper == lower:
		scores = [0.0] * len(raw)
	else:
		scores = [(value - lower) / (upper - lower) for value in raw]
	return scores, [bool(value == -1) for value in model.predict(features)]


def _donation_features(records: Sequence[Mapping[str, Any]]) -> tuple[list[list[float]], list[dict[str, Any]]]:
	by_donor: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
	for record in records:
		donor_id = _text(record.get("donor_id"))
		if donor_id:
			by_donor[donor_id].append(record)
	features: list[list[float]] = []
	metadata: list[dict[str, Any]] = []
	for record in records:
		donor_id = _text(record.get("donor_id"))
		donor_records = by_donor.get(donor_id, [record])
		amounts = [amount for amount in (_number(item.get("amount")) for item in donor_records) if amount is not None]
		amount = _number(record.get("amount")) or 0.0
		dates = [day for day in (_date(item.get("date")) for item in donor_records) if day is not None]
		span_days = max((max(dates) - min(dates)).days, 1) if dates else 1
		features.append([
			amount,
			float(len(donor_records)),
			sum(amounts),
			sum(amounts) / len(amounts) if amounts else 0.0,
			max(amounts, default=0.0),
			min(amounts, default=0.0),
			float(len({_text(item.get("case_id")) for item in donor_records if _text(item.get("case_id"))})),
			len(donor_records) / span_days,
		])
		metadata.append({"amounts": amounts, "donor_count": len(donor_records)})
	return features, metadata


def _case_features(records: Sequence[Mapping[str, Any]]) -> tuple[list[list[float]], list[dict[str, Any]]]:
	features: list[list[float]] = []
	metadata: list[dict[str, Any]] = []
	for record in records:
		estimated = _number(record.get("estimated_funding"))
		current = _number(record.get("current_funding"))
		people = _number(record.get("people_affected")) or 0.0
		goal = estimated or 0.0
		raised = current or 0.0
		gap = max(goal - raised, 0.0)
		features.append([goal, raised, gap, gap / goal if goal > 0 else 0.0, people])
		metadata.append({"estimated": estimated, "current": current, "gap": gap})
	return features, metadata


def detect_anomalies(
	records: Iterable[Mapping[str, Any]],
	*,
	entity_type: str = "donation",
	contamination: float = DEFAULT_CONTAMINATION,
	n_estimators: int = DEFAULT_ESTIMATORS,
	random_state: int = DEFAULT_RANDOM_STATE,
) -> list[dict[str, Any]]:
	"""Detect numerical anomalies in donations or cases.

	Supported ``entity_type`` values are ``donation`` and ``case``. Invalid
	optional numeric fields are represented as neutral values and receive an
	explicit data-quality signal instead of crashing the full run.
	"""

	_validate_configuration(contamination, n_estimators)
	rows = [dict(record) for record in records]
	if entity_type not in {"donation", "case"}:
		raise ValueError("entity_type must be 'donation' or 'case'")
	if not rows:
		return []
	builder = _donation_features if entity_type == "donation" else _case_features
	features, metadata = builder(rows)
	scores, flags = _isolation_scores(features, contamination, n_estimators, random_state)
	results: list[dict[str, Any]] = []
	for index, record in enumerate(rows):
		entity_id = _text(record.get("donation_id" if entity_type == "donation" else "case_id")) or f"record-{index}"
		signals: list[dict[str, Any]] = []
		if entity_type == "donation":
			amount = _number(record.get("amount"))
			amounts = metadata[index]["amounts"]
			if amount is None:
				signals.append(_signal("malformed_amount", "MEDIUM", "Donation amount is missing or not numeric."))
			elif len(amounts) >= 4:
				average = sum(amounts) / len(amounts)
				if average > 0 and amount > average * 3:
					signals.append(_signal("unusual_donation_amount", "HIGH", "Donation amount is unusually high compared with this donor's observed donations."))
			if flags[index]:
				signals.append(_signal("numeric_activity_outlier", "MEDIUM", "Donation activity differs from the observed donation distribution."))
		else:
			estimated = metadata[index]["estimated"]
			current = metadata[index]["current"]
			if estimated is None or current is None:
				signals.append(_signal("malformed_funding", "MEDIUM", "Case funding fields are missing or not numeric."))
			elif current < 0 or estimated <= 0 or current > estimated:
				signals.append(_signal("inconsistent_funding", "HIGH", "Case funding values are internally inconsistent and need review."))
			if flags[index]:
				signals.append(_signal("numeric_case_outlier", "MEDIUM", "Case funding or population values differ from the observed case distribution."))
		score = max(scores[index], 0.8 if any(signal["severity"] == "HIGH" for signal in signals) else 0.0)
		results.append(_result(entity_id, entity_type, score, signals))
	return results


def detect_similar_cases(
	cases: Iterable[Mapping[str, Any]],
	*,
	threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> list[dict[str, Any]]:
	"""Find exact or TF-IDF cosine-similar case description pairs."""

	if not 0.0 <= threshold <= 1.0:
		raise AnomalyConfigurationError("similarity threshold must be between 0 and 1")
	rows = [dict(case) for case in cases]
	descriptions = [(index, _text(row.get("case_id")), normalize_description(row.get("description"))) for index, row in enumerate(rows)]
	pairs: list[SimilarityPair] = []
	exact_groups: dict[str, list[tuple[int, str]]] = defaultdict(list)
	for index, case_id, text in descriptions:
		if text:
			exact_groups[text].append((index, case_id))
	compared: set[tuple[int, int]] = set()
	for group in exact_groups.values():
		for left in range(len(group)):
			for right in range(left + 1, len(group)):
				first, second = group[left], group[right]
				compared.add((first[0], second[0]))
				if first[1] and second[1]:
					pairs.append(SimilarityPair(first[1], second[1], 1.0, True, "Case description is an exact duplicate of another case."))
	usable = [(index, case_id, text) for index, case_id, text in descriptions if case_id and len(text) >= 3]
	if len(usable) >= 2:
		try:
			from sklearn.feature_extraction.text import TfidfVectorizer
			from sklearn.metrics.pairwise import cosine_similarity
			matrix = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform([item[2] for item in usable])
			similarities = cosine_similarity(matrix)
			for left in range(len(usable)):
				for right in range(left + 1, len(usable)):
					original_pair = (usable[left][0], usable[right][0])
					score = float(similarities[left, right])
					if score >= threshold and original_pair not in compared:
						pairs.append(SimilarityPair(usable[left][1], usable[right][1], round(score, 6), False, "Case description is highly similar to another submitted case."))
		except ValueError:
			pass
	pairs.sort(key=lambda pair: (-pair.similarity_score, pair.case_id, pair.matched_case_id))
	return [pair.as_dict() for pair in pairs]


def attach_similarity_signals(
	results: Iterable[Mapping[str, Any]],
	similar_pairs: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
	"""Add pair evidence to case results without changing source records."""

	output = [dict(result) for result in results]
	by_id = {result["entity_id"]: result for result in output}
	for pair in similar_pairs:
		for entity_id, matched_id in ((pair["case_id"], pair["matched_case_id"]), (pair["matched_case_id"], pair["case_id"])):
			result = by_id.get(entity_id)
			if result is None:
				continue
			exact = bool(pair.get("exact"))
			signal = _signal(
				"duplicate_case" if exact else "similar_case",
				"HIGH" if exact else "MEDIUM",
				pair["reason"],
				matched_entity_id=matched_id,
				similarity_score=pair["similarity_score"],
			)
			result.setdefault("signals", []).append(signal)
			result["anomaly_score"] = max(result.get("anomaly_score", 0.0), 0.9 if exact else float(pair["similarity_score"]))
			result["risk_level"] = "HIGH" if result["anomaly_score"] >= 0.75 else "MEDIUM"
			result["is_anomaly"] = True
			result["human_review_recommended"] = True
	return output


def analyze_dataset(
	cases: Iterable[Mapping[str, Any]],
	donations: Iterable[Mapping[str, Any]],
	donors: Iterable[Mapping[str, Any]] | None = None,
	*,
	contamination: float = DEFAULT_CONTAMINATION,
	n_estimators: int = DEFAULT_ESTIMATORS,
	random_state: int = DEFAULT_RANDOM_STATE,
	similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> dict[str, Any]:
	"""Analyze the supported project records and return a JSON-safe report."""

	case_rows, donation_rows = list(cases), list(donations)
	case_results = detect_anomalies(case_rows, entity_type="case", contamination=contamination, n_estimators=n_estimators, random_state=random_state)
	donation_results = detect_anomalies(donation_rows, entity_type="donation", contamination=contamination, n_estimators=n_estimators, random_state=random_state)
	pairs = detect_similar_cases(case_rows, threshold=similarity_threshold)
	case_results = attach_similarity_signals(case_results, pairs)
	return {
		"cases": case_results,
		"donations": donation_results,
		"similar_case_pairs": pairs,
		"donor_count": len(list(donors)) if donors is not None else 0,
	}
