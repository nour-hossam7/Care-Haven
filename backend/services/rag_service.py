from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


_pipeline: Any | None = None


def _get_pipeline() -> Any:
    global _pipeline
    if _pipeline is None:
        from ai.rag.generator import RAGPipeline

        _pipeline = RAGPipeline()
    return _pipeline


def ask_question(question: str, pipeline: Any | None = None) -> dict[str, Any]:
    """Answer a question with the existing Person 2 hybrid RAG pipeline.

    Ollama is contacted lazily inside the pipeline. When it is unavailable the
    pipeline returns a controlled response whose ``error`` is set; that is
    converted into a stable 503 so the backend never crashes.
    """

    rag = pipeline if pipeline is not None else _get_pipeline()
    try:
        response = rag.ask_hybrid(question)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI assistant is temporarily unavailable. Please try again later.",
        ) from exc

    if response.error or response.answer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI assistant is temporarily unavailable. Please try again later.",
        )

    return {
        "answer": response.answer,
        "sources": [dict(source) for source in (response.sources or [])],
    }