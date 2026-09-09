"""Persistent ChromaDB storage for trusted humanitarian knowledge chunks."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Iterable

from .chunking import TextChunk

LOGGER = logging.getLogger(__name__)
DEFAULT_CHROMA_DIR = Path(__file__).resolve().parents[2] / "data" / "rag_documents" / "chroma"
DEFAULT_COLLECTION = "carehaven_humanitarian_knowledge"


class VectorStoreError(RuntimeError):
	"""Raised when persistent vector storage cannot be used."""


class ChromaVectorStore:
	"""A small wrapper around one persistent ChromaDB collection."""

	def __init__(
		self,
		persist_directory: str | Path | None = None,
		collection_name: str | None = None,
		*,
		client: Any | None = None,
	) -> None:
		self.persist_directory = Path(persist_directory or os.getenv("CAREHAVEN_CHROMA_DIR", DEFAULT_CHROMA_DIR)).resolve()
		self.collection_name = collection_name or os.getenv("CAREHAVEN_CHROMA_COLLECTION", DEFAULT_COLLECTION)
		self._client = client
		self._collection: Any | None = None

	@property
	def collection(self) -> Any:
		if self._collection is None:
			if self._client is None:
				try:
					import chromadb
				except ImportError as exc:
					raise VectorStoreError("ChromaDB is required for vector storage. Install chromadb.") from exc
				self.persist_directory.mkdir(parents=True, exist_ok=True)
				try:
					self._client = chromadb.PersistentClient(path=str(self.persist_directory))
				except Exception as exc:
					raise VectorStoreError(f"Could not initialize ChromaDB at {self.persist_directory}: {exc}") from exc
			try:
				self._collection = self._client.get_or_create_collection(name=self.collection_name)
			except Exception as exc:
				raise VectorStoreError(f"Could not open ChromaDB collection {self.collection_name}: {exc}") from exc
		return self._collection

	@staticmethod
	def _metadata(chunk: TextChunk) -> dict[str, Any]:
		metadata: dict[str, Any] = {
			"source": chunk.source,
			"source_path": chunk.source_path,
			"document_name": chunk.document_name,
			"page": chunk.page if chunk.page is not None else -1,
			"chunk_id": chunk.chunk_id,
		}
		for key, value in chunk.metadata.items():
			if isinstance(value, (str, int, float, bool)) or value is None:
				metadata[key] = value if value is not None else ""
		return metadata

	def upsert(self, chunks: Iterable[TextChunk], embeddings: Iterable[list[float]]) -> int:
		"""Upsert chunks and vectors by deterministic chunk ID."""

		chunk_list = list(chunks)
		vector_list = list(embeddings)
		if len(chunk_list) != len(vector_list):
			raise ValueError("chunks and embeddings must have equal lengths")
		if not chunk_list:
			return 0
		try:
			self.collection.upsert(
				ids=[chunk.chunk_id for chunk in chunk_list],
				documents=[chunk.text for chunk in chunk_list],
				embeddings=vector_list,
				metadatas=[self._metadata(chunk) for chunk in chunk_list],
			)
		except Exception as exc:
			raise VectorStoreError(f"Could not upsert RAG chunks: {exc}") from exc
		return len(chunk_list)

	def query(self, embedding: list[float], *, top_k: int = 5, where: dict[str, Any] | None = None) -> dict[str, Any]:
		"""Query nearest chunks, returning Chroma's result structure."""

		if top_k <= 0:
			raise ValueError("top_k must be greater than zero")
		try:
			return self.collection.query(
				query_embeddings=[embedding], n_results=top_k, where=where,
				include=["documents", "metadatas", "distances"],
			)
		except Exception as exc:
			raise VectorStoreError(f"Could not query RAG vector store: {exc}") from exc

	def count(self) -> int:
		"""Return the number of indexed chunks."""

		try:
			return int(self.collection.count())
		except Exception as exc:
			raise VectorStoreError(f"Could not count RAG chunks: {exc}") from exc

	def get_chunks(self) -> list[dict[str, Any]]:
		"""Return indexed documents and metadata for local lexical retrieval."""

		if not hasattr(self.collection, "get"):
			return []
		try:
			result = self.collection.get(include=["documents", "metadatas"])
		except Exception as exc:
			raise VectorStoreError(f"Could not read RAG chunks: {exc}") from exc
		ids = result.get("ids") or []
		documents = result.get("documents") or []
		metadatas = result.get("metadatas") or []
		return [
			{"chunk_id": str(chunk_id), "text": str(documents[index]), "metadata": dict(metadatas[index] or {})}
			for index, chunk_id in enumerate(ids)
			if index < len(documents)
		]

	def reset(self) -> None:
		"""Delete and recreate this collection explicitly."""

		try:
			self._client.delete_collection(name=self.collection_name)
		except Exception as exc:
			raise VectorStoreError(f"Could not delete RAG collection {self.collection_name}: {exc}") from exc
		self._collection = None
