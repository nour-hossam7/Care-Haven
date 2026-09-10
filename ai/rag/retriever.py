"""Semantic retrieval and grounded context construction."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .embeddings import SentenceTransformerEmbeddings
from .vector_store import ChromaVectorStore

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetrievedChunk:
	"""One ranked chunk returned by semantic retrieval."""

	chunk_id: str
	text: str
	source: str | None
	document_name: str | None
	page: int | None
	distance: float
	metadata: dict[str, Any] = field(default_factory=dict)


class Retriever:
	"""Retrieve relevant trusted knowledge independently from an LLM."""

	def __init__(
		self,
		vector_store: ChromaVectorStore | None = None,
		embedder: SentenceTransformerEmbeddings | Any | None = None,
		*,
		top_k: int = 5,
		score_threshold: float | None = None,
	) -> None:
		if top_k <= 0:
			raise ValueError("top_k must be greater than zero")
		self.vector_store = vector_store or ChromaVectorStore()
		self.embedder = embedder or SentenceTransformerEmbeddings()
		self.top_k = top_k
		self.score_threshold = score_threshold

	def retrieve(self, query: str, *, top_k: int | None = None) -> list[RetrievedChunk]:
		"""Return ranked chunks, filtering distances above the configured threshold."""

		if not query or not query.strip():
			raise ValueError("query must not be empty")
		if self.vector_store.count() == 0:
			return []
		requested = top_k or self.top_k
		if requested <= 0:
			raise ValueError("top_k must be greater than zero")
		result = self.vector_store.query(self.embedder.encode_query(query), top_k=requested)
		ids = (result.get("ids") or [[]])[0]
		documents = (result.get("documents") or [[]])[0]
		metadatas = (result.get("metadatas") or [[]])[0]
		distances = (result.get("distances") or [[]])[0]
		retrieved: list[RetrievedChunk] = []
		for index, chunk_id in enumerate(ids):
			distance = float(distances[index]) if index < len(distances) else float("inf")
			if self.score_threshold is not None and distance > self.score_threshold:
				continue
			metadata = dict(metadatas[index] or {}) if index < len(metadatas) else {}
			page_value = metadata.get("page")
			page = None if page_value in (None, "", -1, "-1") else int(page_value)
			retrieved.append(
				RetrievedChunk(
					chunk_id=str(chunk_id),
					text=str(documents[index]) if index < len(documents) else "",
					source=metadata.get("source"),
					document_name=metadata.get("document_name"),
					page=page,
					distance=distance,
					metadata=metadata,
				)
			)
		retrieved.sort(key=lambda item: (item.distance, item.chunk_id))
		LOGGER.info("Retrieved %s chunk(s) for query", len(retrieved))
		return retrieved

	@staticmethod
	def build_context(chunks: list[RetrievedChunk], *, max_characters: int = 12000) -> str:
		"""Format only retrieved chunks into bounded, source-labelled context."""

		if max_characters <= 0:
			raise ValueError("max_characters must be greater than zero")
		sections: list[str] = []
		used = 0
		for index, chunk in enumerate(chunks, start=1):
			page = str(chunk.page) if chunk.page is not None else "Unavailable"
			section = f"SOURCE {index}\nDocument: {chunk.document_name or 'Unavailable'}\nPage: {page}\nContent:\n{chunk.text}"
			separator = "\n\n" if sections else ""
			if used + len(separator) + len(section) > max_characters:
				break
			sections.append(section)
			used += len(separator) + len(section)
		return "\n\n".join(sections)
