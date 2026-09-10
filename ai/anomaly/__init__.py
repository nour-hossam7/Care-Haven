"""Review-oriented anomaly and suspicious-activity signals."""

from .detector import (
	analyze_dataset,
	attach_similarity_signals,
	detect_anomalies,
	detect_similar_cases,
	normalize_description,
)

__all__ = [
	"analyze_dataset",
	"attach_similarity_signals",
	"detect_anomalies",
	"detect_similar_cases",
	"normalize_description",
]
