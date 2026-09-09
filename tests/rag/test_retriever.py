from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ai.rag.chunking import TextChunk, chunk_pages
from ai.rag.generator import RAGPipeline
from ai.rag.ingestion import DocumentIngestor, SourcePage, clean_text
from ai.rag.retriever import Retriever
from ai.rag.vector_store import ChromaVectorStore


class FakeEmbedder:
	def encode_documents(self, texts: list[str]) -> list[list[float]]:
		return [[float(len(text))] for text in texts]

	def encode_query(self, query: str) -> list[float]:
		return [float(len(query))]


class FakeCollection:
	def __init__(self) -> None:
		self.items: dict[str, dict[str, Any]] = {}

	def upsert(self, *, ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict[str, Any]]) -> None:
		for chunk_id, document, embedding, metadata in zip(ids, documents, embeddings, metadatas):
			self.items[chunk_id] = {"document": document, "embedding": embedding, "metadata": metadata}

	def count(self) -> int:
		return len(self.items)

	def query(self, *, query_embeddings: list[list[float]], n_results: int, where: Any = None, include: Any = None) -> dict[str, Any]:
		query_value = query_embeddings[0][0]
		ranked = sorted(self.items.items(), key=lambda item: (abs(item[1]["embedding"][0] - query_value), item[0]))[:n_results]
		return {
			"ids": [[item[0] for item in ranked]],
			"documents": [[item[1]["document"] for item in ranked]],
			"metadatas": [[item[1]["metadata"] for item in ranked]],
			"distances": [[abs(item[1]["embedding"][0] - query_value) for item in ranked]],
		}


class FakeClient:
	def __init__(self) -> None:
		self.collections: dict[str, FakeCollection] = {}

	def get_or_create_collection(self, *, name: str) -> FakeCollection:
		return self.collections.setdefault(name, FakeCollection())

	def delete_collection(self, *, name: str) -> None:
		self.collections.pop(name, None)


class FakeGenerator:
	def generate(self, question: str, chunks: list[Any]) -> str:
		assert question
		assert chunks
		return "Grounded answer."


def make_page(text: str, page: int = 3) -> SourcePage:
	return SourcePage(
		text=text,
		source="https://example.test/guidance",
		source_path="data/raw/documents/rag/guidance.pdf",
		document_name="guidance.pdf",
		file_type="pdf",
		page=page,
	)


def test_clean_text_and_chunk_ids_are_deterministic() -> None:
	page = make_page("Heading\n\nA meaningful paragraph with  extra spaces.")
	assert clean_text("A\u00a0  B\n\n\nC") == "A B\n\nC"
	first = chunk_pages([page], chunk_size=80, overlap=10)
	second = chunk_pages([page], chunk_size=80, overlap=10)
	assert first and first[0].chunk_id == second[0].chunk_id
	assert first[0].page == 3
	assert first[0].metadata["source"] == page.source


def test_empty_text_is_not_chunked() -> None:
	assert chunk_pages([make_page("   ")]) == []


def test_retrieval_returns_relevant_metadata_and_empty_store_is_safe() -> None:
	client = FakeClient()
	store = ChromaVectorStore(client=client)
	chunk = chunk_pages([make_page("Emergency needs assessment considers affected people and resources.")])[0]
	store.upsert([chunk], [[len(chunk.text)]])
	retriever = Retriever(store, FakeEmbedder(), top_k=2)
	results = retriever.retrieve("Emergency needs assessment")
	assert len(results) == 1
	assert results[0].page == 3
	assert results[0].source == "https://example.test/guidance"
	assert Retriever(ChromaVectorStore(client=FakeClient()), FakeEmbedder()).retrieve("anything") == []


def test_repeated_pipeline_indexing_is_idempotent(tmp_path: Path) -> None:
	source = tmp_path / "knowledge.txt"
	source.write_text("Emergency planning should assess needs and available resources.", encoding="utf-8")
	store = ChromaVectorStore(client=FakeClient())
	pipeline = RAGPipeline(
		ingestor=DocumentIngestor(tmp_path),
		embedder=FakeEmbedder(),
		vector_store=store,
		generator=lambda question, context: "unused",
	)
	first = pipeline.build_index(chunk_size=100, overlap=10)
	second = pipeline.build_index(chunk_size=100, overlap=10)
	assert first["chunks_indexed"] == second["chunks_indexed"] == 1
	assert first["indexed_total"] == second["indexed_total"] == 1


def test_context_preserves_sources_and_has_a_limit() -> None:
	client = FakeClient()
	store = ChromaVectorStore(client=client)
	chunk = chunk_pages([make_page("Relevant humanitarian guidance.")])[0]
	store.upsert([chunk], [[1.0]])
	result = Retriever(store, FakeEmbedder()).retrieve("Relevant")
	context = Retriever.build_context(result, max_characters=500)
	assert "SOURCE 1" in context
	assert "Page: 3" in context
	assert "Relevant humanitarian guidance." in context


def test_pipeline_answer_exposes_only_retrieved_sources() -> None:
	client = FakeClient()
	store = ChromaVectorStore(client=client)
	chunk = chunk_pages([make_page("Relevant humanitarian guidance.")])[0]
	store.upsert([chunk], [[1.0]])
	pipeline = RAGPipeline(vector_store=store, embedder=FakeEmbedder(), generator=FakeGenerator())
	response = pipeline.ask("Relevant")
	assert response.answer == "Grounded answer."
	assert response.sources == [
		{
			"document": "guidance.pdf",
			"page": 3,
			"source": "https://example.test/guidance",
			"chunk_id": chunk.chunk_id,
		}
	]


def test_real_source_document_has_page_aware_text() -> None:
	source_dir = Path("data/raw/documents/rag")
	if not (source_dir / "ifrc_emergency_needs_assessment_and_planning_2025.pdf").exists():
		pytest.skip("trusted source PDF is not present")
	pages = DocumentIngestor(source_dir).ingest_all()
	assert len(pages) == 68
	assert pages[0].page == 1
	assert pages[-1].page == 68
