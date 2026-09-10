from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)


class ChatSource(BaseModel):
    document: str | None = None
    page: int | None = None
    source: str | None = None
    chunk_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = []