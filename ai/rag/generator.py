"""Grounded Ollama generation and the high-level CareHaven RAG pipeline."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Iterable

import requests

from .chunking import TextChunk, chunk_pages
from .embeddings import SentenceTransformerEmbeddings
from .ingestion import DocumentIngestor
from .retriever import RetrievedChunk, Retriever
from .vector_store import ChromaVectorStore

LOGGER = logging.getLogger(__name__)
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3:4b"
NO_CONTEXT_ANSWER = (
	"The available CareHaven knowledge sources do not contain enough information "
	"to answer this question."
)


class GenerationError(RuntimeError):
	"""Raised when Ollama cannot produce a valid response."""


@dataclass(frozen=True)
class RAGResponse:
	"""Public answer, traceable sources, and retrieval evidence."""

	answer: str | None
	sources: list[dict[str, Any]]
	retrieved_chunks: list[RetrievedChunk]
	context: str
	error: str | None = None


@dataclass(frozen=True)
class GenerationResult:
	"""Application-level result from the grounded generation step."""

	answer: str | None
	error: str | None = None


class OllamaGenerator:
	"""Call Ollama's local generate endpoint with a grounded prompt."""

	def __init__(self, base_url: str | None = None, model: str | None = None, *, timeout: float = 60.0) -> None:
		self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)).rstrip("/")
		self.model = model or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
		self.timeout = timeout

	@staticmethod
	def _build_prompt(question: str, chunks: Iterable[RetrievedChunk]) -> str:
		sections: list[str] = []
		for index, chunk in enumerate(chunks, start=1):
			page = str(chunk.page) if chunk.page is not None else "Unavailable"
			sections.append(
				f"[Source {index}]\n"
				f"Document: {chunk.document_name or 'Unavailable'}\n"
				f"Source: {chunk.source or 'Unavailable'}\n"
				f"Page: {page}\n"
				f"Chunk ID: {chunk.chunk_id}\n"
				f"Content:\n{chunk.text}"
			)
		context = "\n\n".join(sections)
		return (
			"SYSTEM:\n"
			"You are CareHaven's humanitarian knowledge assistant.\n"
			"Answer using ONLY the supplied context. Do not invent facts, sources, or citations.\n"
			"If the context does not contain enough information, explicitly say that the available "
			"sources do not provide enough information. Do not pretend to have accessed sources that "
			"were not retrieved. Prefer concise, useful answers and preserve important terminology.\n\n"
			f"CONTEXT:\n{context}\n\n"
			f"USER QUESTION:\n{question.strip()}\n\n"
			"ANSWER:"
		)

	def generate(self, question: str, chunks: Iterable[RetrievedChunk]) -> GenerationResult:
		"""Generate an answer strictly grounded in retrieved chunks."""

		if not question or not question.strip():
			raise ValueError("question must not be empty")
		chunk_list = list(chunks)
		if not any(chunk.text.strip() for chunk in chunk_list):
			return GenerationResult(answer=NO_CONTEXT_ANSWER)
		prompt = self._build_prompt(question, chunk_list)
		try:
			response = requests.post(
				f"{self.base_url}/api/generate",
				json={"model": self.model, "prompt": prompt, "stream": False},
				timeout=self.timeout,
			)
			response.raise_for_status()
			payload = response.json()
		except requests.RequestException as exc:
			return GenerationResult(answer=None, error=f"Ollama is unavailable at {self.base_url}: {exc}")
		except ValueError as exc:
			return GenerationResult(answer=None, error=f"Ollama returned invalid JSON: {exc}")
		answer = payload.get("response") if isinstance(payload, dict) else None
		if not isinstance(answer, str) or not answer.strip():
			return GenerationResult(answer=None, error="Ollama response did not contain a non-empty 'response' field")
		return GenerationResult(answer=answer.strip())


class RAGPipeline:
	"""Explicitly indexed and queryable RAG pipeline for trusted documents."""

	def __init__(
		self,
		*,
		ingestor: DocumentIngestor | None = None,
		embedder: SentenceTransformerEmbeddings | Any | None = None,
		vector_store: ChromaVectorStore | None = None,
		generator: OllamaGenerator | Any | None = None,
		top_k: int = 5,
		score_threshold: float | None = None,
		max_context_characters: int = 12000,
	) -> None:
		self.ingestor = ingestor or DocumentIngestor()
		self.embedder = embedder or SentenceTransformerEmbeddings()
		self.vector_store = vector_store or ChromaVectorStore()
		self.retriever = Retriever(
			self.vector_store, self.embedder, top_k=top_k, score_threshold=score_threshold,
		)
		self.generator = generator or OllamaGenerator()
		self.max_context_characters = max_context_characters

	def build_index(self, *, strict: bool = True, chunk_size: int = 1200, overlap: int = 150) -> dict[str, int]:
		"""Ingest, chunk, embed, and upsert all trusted RAG documents."""

		paths = self.ingestor.discover_documents()
		pages = self.ingestor.ingest_all(strict=strict)
		chunks: list[TextChunk] = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)
		embeddings = self.embedder.encode_documents([chunk.text for chunk in chunks])
		indexed = self.vector_store.upsert(chunks, embeddings)
		stats = {
			"documents_discovered": len(paths),
			"pages_extracted": len(pages),
			"chunks_created": len(chunks),
			"chunks_indexed": indexed,
			"indexed_total": self.vector_store.count(),
		}
		LOGGER.info("RAG index statistics: %s", stats)
		return stats

	def retrieve(self, question: str, *, top_k: int | None = None) -> list[RetrievedChunk]:
		"""Retrieve evidence without calling Ollama."""

		return self.retriever.retrieve(question, top_k=top_k)

	def ask(self, question: str) -> RAGResponse:
		"""Retrieve evidence, build context, and generate a grounded answer."""

		chunks = self.retrieve(question)
		context = self.retriever.build_context(chunks, max_characters=self.max_context_characters)
		sources = [
			{"document": chunk.document_name, "page": chunk.page, "source": chunk.source, "chunk_id": chunk.chunk_id}
			for chunk in chunks
		]
		result = self.generator.generate(question, chunks)
		if isinstance(result, GenerationResult):
			return RAGResponse(
				answer=result.answer, sources=sources, retrieved_chunks=chunks, context=context, error=result.error,
			)
		return RAGResponse(answer=result, sources=sources, retrieved_chunks=chunks, context=context)
