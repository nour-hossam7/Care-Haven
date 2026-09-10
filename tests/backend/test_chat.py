from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.main import app
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services import rag_service


class FakePipeline:
    def __init__(self, answer="A helpful answer", sources=None, error=None):
        self.answer = answer
        self.sources = sources or [{"document": "Handbook", "page": 3, "source": "manual", "chunk_id": "abc"}]
        self.error = error

    def ask_hybrid(self, question):
        return SimpleNamespace(answer=self.answer, sources=self.sources, error=self.error)


def test_rag_service_returns_answer_and_sources():
    result = rag_service.ask_question("What is care haven?", FakePipeline())

    assert result["answer"] == "A helpful answer"
    assert result["sources"][0]["document"] == "Handbook"


def test_rag_service_returns_503_when_ollama_unavailable():
    pipeline = FakePipeline(answer=None, error="Ollama is unavailable at http://localhost:11434")

    with pytest.raises(HTTPException) as exc_info:
        rag_service.ask_question("What is care haven?", pipeline)

    assert exc_info.value.status_code == 503


def test_rag_service_returns_503_when_generation_crashes():
    class ExplodingPipeline:
        def ask_hybrid(self, question):
            raise ConnectionError("ollama down")

    with pytest.raises(HTTPException) as exc_info:
        rag_service.ask_question("What is care haven?", ExplodingPipeline())

    assert exc_info.value.status_code == 503


def test_chat_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ChatRequest(question="hello", query="extra")


def test_chat_request_rejects_empty_question():
    with pytest.raises(ValidationError):
        ChatRequest(question="")


def test_chat_response_accepts_answer_and_sources():
    response = ChatResponse(answer="hello", sources=[{"document": "x", "page": 1, "source": "y", "chunk_id": "z"}])
    assert response.answer == "hello"
    assert len(response.sources) == 1


def test_chat_endpoint_requires_authentication():
    response = TestClient(app).post("/chat", json={"question": "hello"})
    assert response.status_code == 401