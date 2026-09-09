from __future__ import annotations

import json
from typing import Any

import requests
from pydantic import ValidationError

from backend.core.config import settings

from .schemas import CaseAnalysisResult


class LLMIntegrationError(RuntimeError):
    """A controlled failure returned by the local LLM integration."""


class LLMUnavailableError(LLMIntegrationError):
    pass


class LLMTimeoutError(LLMIntegrationError):
    pass


class LLMResponseError(LLMIntegrationError):
    pass


class OllamaCaseAnalysisClient:
    """Small, injectable client for Ollama's non-streaming generate API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout

    @staticmethod
    def _prompt(case_data: dict[str, Any]) -> str:
        return (
            "You extract structured information from humanitarian case reports. "
            "Return only a JSON object with exactly these fields: category (string), "
            "assistance (non-empty array of strings), people_affected (positive integer), "
            "severity (one of Low, Medium, High, Critical), and summary (string). "
            "Do not include Markdown, explanations, or fields that were not requested.\n\n"
            f"CASE DATA:\n{json.dumps(case_data, ensure_ascii=False, default=str)}"
        )

    @staticmethod
    def _parse_response(payload: object) -> CaseAnalysisResult:
        if not isinstance(payload, dict):
            raise LLMResponseError("LLM response must be a JSON object")
        response_text = payload.get("response")
        if not isinstance(response_text, str) or not response_text.strip():
            raise LLMResponseError("LLM response did not contain a non-empty 'response' field")
        try:
            structured = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise LLMResponseError("LLM response was not valid JSON") from exc
        try:
            return CaseAnalysisResult.model_validate(structured)
        except ValidationError as exc:
            raise LLMResponseError("LLM response did not match the required analysis structure") from exc

    def analyze(self, case_data: dict[str, Any]) -> CaseAnalysisResult:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": self._prompt(case_data), "stream": False},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise LLMTimeoutError("LLM request timed out") from exc
        except requests.RequestException as exc:
            raise LLMUnavailableError("LLM service is unavailable") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise LLMResponseError("LLM returned invalid JSON") from exc
        return self._parse_response(payload)
