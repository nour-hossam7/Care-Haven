"""Lazy Sentence Transformers embedding support for RAG documents and queries."""

from __future__ import annotations

import logging
import os
from typing import Any, Sequence

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingError(RuntimeError):
	"""Raised when the configured embedding backend is unavailable."""


class SentenceTransformerEmbeddings:
	"""Reusable lazy-loaded Sentence Transformers encoder."""

	def __init__(self, model_name: str | None = None) -> None:
		self.model_name = model_name or os.getenv("CAREHAVEN_EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
		self._model: Any | None = None

	def _get_model(self) -> Any:
		if self._model is None:
			try:
				from sentence_transformers import SentenceTransformer
			except ImportError as exc:
				raise EmbeddingError(
					"Sentence Transformers is required for embeddings. Install sentence-transformers."
				) from exc
			LOGGER.info("Loading embedding model %s", self.model_name)
			try:
				self._model = SentenceTransformer(self.model_name)
			except Exception as exc:
				raise EmbeddingError(f"Could not load embedding model {self.model_name}: {exc}") from exc
		return self._model

	def encode_documents(self, texts: Sequence[str]) -> list[list[float]]:
		"""Encode document texts into JSON-compatible vectors."""

		return self._encode(texts, is_query=False)

	def encode_query(self, query: str) -> list[float]:
		"""Encode one query into a JSON-compatible vector."""

		if not query or not query.strip():
			raise ValueError("query must not be empty")
		return self._encode([query], is_query=True)[0]

	def _encode(self, texts: Sequence[str], *, is_query: bool) -> list[list[float]]:
		if any(not text or not text.strip() for text in texts):
			raise ValueError("texts must not contain empty values")
		if not texts:
			return []
		model = self._get_model()
		try:
			if is_query and hasattr(model, "encode_query"):
				vectors = model.encode_query(list(texts), normalize_embeddings=True)
			elif not is_query and hasattr(model, "encode_document"):
				vectors = model.encode_document(list(texts), normalize_embeddings=True)
			else:
				vectors = model.encode(list(texts), normalize_embeddings=True)
		except Exception as exc:
			raise EmbeddingError(f"Embedding generation failed: {exc}") from exc
		return [list(map(float, vector)) for vector in vectors]
