from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import requests

from ai.rag.generator import NO_CONTEXT_ANSWER, OllamaGenerator
from ai.rag.retriever import RetrievedChunk


def make_chunk() -> RetrievedChunk:
	return RetrievedChunk(
		chunk_id="chunk-123",
		text="Emergency needs assessment gathers information about affected people and resources.",
		source="IFRC guidance",
		document_name="ifrc_guidance.pdf",
		page=10,
		distance=0.12,
		metadata={"source": "IFRC guidance", "page": 10, "chunk_id": "chunk-123"},
	)


def response(payload: Any = None, *, status_code: int = 200) -> Mock:
	result = Mock()
	result.raise_for_status.side_effect = requests.HTTPError("bad response") if status_code >= 400 else None
	result.json.return_value = payload
	return result


def test_success_uses_configured_ollama_url_model_and_grounded_prompt() -> None:
	generator = OllamaGenerator(base_url="http://ollama.test/", model="qwen3:4b", timeout=9)
	with patch("ai.rag.generator.requests.post", return_value=response({"response": "Grounded answer."})) as post:
		result = generator.generate("What is assessed?", [make_chunk()])

	assert result.answer == "Grounded answer."
	assert result.error is None
	post.assert_called_once()
	url, = post.call_args.args
	payload = post.call_args.kwargs["json"]
	assert url == "http://ollama.test/api/generate"
	assert payload["model"] == "qwen3:4b"
	assert payload["stream"] is False
	assert "Emergency needs assessment" in payload["prompt"]
	assert "What is assessed?" in payload["prompt"]
	assert "ifrc_guidance.pdf" in payload["prompt"]
	assert "Page: 10" in payload["prompt"]
	assert "Chunk ID: chunk-123" in payload["prompt"]
	assert post.call_args.kwargs["timeout"] == 9


def test_empty_context_does_not_call_ollama() -> None:
	with patch("ai.rag.generator.requests.post") as post:
		result = OllamaGenerator().generate("Unrelated question", [])

	assert result.answer == NO_CONTEXT_ANSWER
	assert result.error is None
	post.assert_not_called()


def test_unavailable_ollama_returns_application_error() -> None:
	with patch("ai.rag.generator.requests.post", side_effect=requests.ConnectionError("offline")):
		result = OllamaGenerator().generate("Question", [make_chunk()])

	assert result.answer is None
	assert result.error is not None
	assert "Ollama is unavailable" in result.error


def test_http_failure_returns_application_error() -> None:
	with patch("ai.rag.generator.requests.post", return_value=response({}, status_code=500)):
		result = OllamaGenerator().generate("Question", [make_chunk()])

	assert result.answer is None
	assert result.error is not None
	assert "Ollama is unavailable" in result.error


def test_malformed_and_empty_responses_return_application_errors() -> None:
	malformed_response = response()
	malformed_response.json.side_effect = ValueError("invalid")
	with patch("ai.rag.generator.requests.post", return_value=malformed_response):
		malformed = OllamaGenerator().generate("Question", [make_chunk()])
	with patch("ai.rag.generator.requests.post", return_value=response({"response": "  "})):
		empty = OllamaGenerator().generate("Question", [make_chunk()])

	assert malformed.answer is None
	assert "invalid JSON" in (malformed.error or "")
	assert empty.answer is None
	assert "non-empty" in (empty.error or "")