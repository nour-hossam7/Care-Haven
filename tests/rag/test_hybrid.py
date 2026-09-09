from __future__ import annotations

from ai.rag.hybrid import BM25Retriever, HybridRetriever
from ai.rag.retriever import RetrievedChunk


class FakeSemanticRetriever:
	def __init__(self, chunks: list[RetrievedChunk]) -> None:
		self.chunks = chunks

	def retrieve(self, query: str, *, top_k: int) -> list[RetrievedChunk]:
		return self.chunks[:top_k]


def chunk(chunk_id: str, text: str, page: int) -> RetrievedChunk:
	return RetrievedChunk(chunk_id, text, "IFRC", "guidance.pdf", page, 0.1, {"source": "IFRC"})


def test_lexical_retrieval_preserves_metadata_and_ranks_matches() -> None:
	results = BM25Retriever([
		chunk("a", "Emergency needs assessment guidance", 10),
		chunk("b", "Donation planning guidance", 20),
	]).retrieve("emergency assessment", top_k=1)

	assert [item.chunk_id for item in results] == ["a"]
	assert results[0].page == 10
	assert results[0].metadata["retrieval_method"] == "lexical_bm25"


def test_hybrid_fuses_duplicate_semantic_and_lexical_results_with_rrf() -> None:
	a = chunk("a", "Emergency needs assessment", 10)
	b = chunk("b", "Emergency planning", 20)
	retriever = HybridRetriever(FakeSemanticRetriever([b, a]), BM25Retriever([a, b]))

	results = retriever.retrieve("emergency", top_k=2)

	assert {item.chunk_id for item in results} == {"a", "b"}
	assert results[0].metadata["retrieval_methods"] == ["lexical", "semantic"]
	assert results[0].metadata["rrf_score"] > results[1].metadata["rrf_score"]


def test_hybrid_supports_only_one_source_and_empty_corpus() -> None:
	a = chunk("a", "Emergency needs assessment", 10)
	semantic_only = HybridRetriever(FakeSemanticRetriever([a]), BM25Retriever([]))
	lexical_only = HybridRetriever(FakeSemanticRetriever([]), BM25Retriever([a]))
	empty = HybridRetriever(FakeSemanticRetriever([]), BM25Retriever([]))

	assert [item.chunk_id for item in semantic_only.retrieve("anything")] == ["a"]
	assert [item.chunk_id for item in lexical_only.retrieve("emergency")] == ["a"]
	assert empty.retrieve("anything") == []


def test_hybrid_top_k_and_order_are_deterministic() -> None:
	chunks = [chunk("b", "emergency", 2), chunk("a", "emergency", 1), chunk("c", "other", 3)]
	retriever = HybridRetriever(FakeSemanticRetriever(chunks), BM25Retriever(chunks))

	first = retriever.retrieve("emergency", top_k=1)
	second = retriever.retrieve("emergency", top_k=1)

	assert len(first) == 1
	assert first == second
	assert first[0].chunk_id == "a"