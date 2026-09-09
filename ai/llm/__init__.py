"""Structured local-LLM analysis support."""

from .client import OllamaCaseAnalysisClient
from .schemas import CaseAnalysisResult

__all__ = ["CaseAnalysisResult", "OllamaCaseAnalysisClient"]
