"""Deterministic, metadata-preserving text chunking for RAG sources."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Iterable

from .ingestion import SourcePage

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TextChunk:
	"""A retrieval unit with stable identity and source traceability."""

	chunk_id: str
	text: str
	source: str
	source_path: str
	document_name: str
	page: int | None
	metadata: dict[str, Any]


def _chunk_id(page: SourcePage, index: int, text: str) -> str:
	key = f"{page.source_path}|{page.page}|{index}|{text}".encode("utf-8")
	return hashlib.sha256(key).hexdigest()


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
	paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
	chunks: list[str] = []
	current = ""
	for paragraph in paragraphs:
		if len(paragraph) <= chunk_size and len(current) + len(paragraph) + 2 <= chunk_size:
			current = f"{current}\n\n{paragraph}".strip()
			continue
		if current:
			chunks.append(current)
		if len(paragraph) <= chunk_size:
			current = paragraph
			continue
		start = 0
		while start < len(paragraph):
			end = min(start + chunk_size, len(paragraph))
			segment = paragraph[start:end].strip()
			if segment:
				chunks.append(segment)
			if end == len(paragraph):
				break
			start = max(end - overlap, start + 1)
		current = ""
	if current:
		chunks.append(current)
	return chunks


def chunk_pages(
	pages: Iterable[SourcePage],
	*,
	chunk_size: int = 1200,
	overlap: int = 150,
) -> list[TextChunk]:
	"""Split source pages into stable, non-empty chunks.

	Chunk boundaries prefer paragraph boundaries and fall back to character
	windows for unusually long paragraphs.
	"""

	if chunk_size <= 0:
		raise ValueError("chunk_size must be greater than zero")
	if overlap < 0 or overlap >= chunk_size:
		raise ValueError("overlap must be non-negative and smaller than chunk_size")

	chunks: list[TextChunk] = []
	for page in pages:
		for index, text in enumerate(_split_text(page.text, chunk_size, overlap)):
			if not text.strip():
				continue
			metadata = dict(page.metadata)
			metadata.update(
				{
					"source": page.source,
					"source_path": page.source_path,
					"document_name": page.document_name,
					"page": page.page,
				}
			)
			chunks.append(
				TextChunk(
					chunk_id=_chunk_id(page, index, text),
					text=text,
					source=page.source,
					source_path=page.source_path,
					document_name=page.document_name,
					page=page.page,
					metadata=metadata,
				)
			)
	LOGGER.info("Created %s RAG chunks", len(chunks))
	return chunks
