"""Local lexical retrieval and deterministic semantic/lexical fusion."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable

from .retriever import RetrievedChunk, Retriever

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
DEFAULT_RRF_K = 60


def _tokens(value: str) -> list[str]:
	return TOKEN_PATTERN.findall(value.casefold())


class BM25Retriever:
	"""Small in-memory BM25-style retriever for an existing chunk corpus."""

	def __init__(self, chunks: Iterable[RetrievedChunk], *, k1: float = 1.5, b: float = 0.75) -> None:
		if k1 < 0 or not 0 <= b <= 1:
			raise ValueError("BM25 k1 must be non-negative and b must be between zero and one")
		self.k1 = k1
		self.b = b
		self._chunks = tuple(sorted(chunks, key=lambda chunk: chunk.chunk_id))
		self._document_tokens = tuple(_tokens(chunk.text) for chunk in self._chunks)
		self._lengths = tuple(len(tokens) for tokens in self._document_tokens)
		self._average_length = sum(self._lengths) / len(self._lengths) if self._lengths else 0.0
		self._document_frequency: Counter[str] = Counter()
		for tokens in self._document_tokens:
			self._document_frequency.update(set(tokens))

	def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
		if not query or not query.strip():
			raise ValueError("query must not be empty")
		if top_k <= 0:
			raise ValueError("top_k must be greater than zero")
		if not self._chunks:
			return []
		query_terms = _tokens(query)
		if not query_terms:
			return []
		document_count = len(self._chunks)
		results: list[tuple[float, RetrievedChunk]] = []
		for chunk, tokens in zip(self._chunks, self._document_tokens):
			term_counts = Counter(tokens)
			score = 0.0
			for term in query_terms:
				term_frequency = term_counts.get(term, 0)
				if not term_frequency:
					continue
				document_frequency = self._document_frequency[term]
				idf = math.log(1 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5))
				normalizer = term_frequency + self.k1 * (
					1 - self.b + self.b * len(tokens) / self._average_length
				)
				score += idf * term_frequency * (self.k1 + 1) / normalizer
			if score > 0:
				metadata = dict(chunk.metadata)
				metadata["retrieval_method"] = "lexical_bm25"
				metadata["lexical_score"] = round(score, 6)
				results.append((score, RetrievedChunk(
					chunk_id=chunk.chunk_id,
					text=chunk.text,
					source=chunk.source,
					document_name=chunk.document_name,
					page=chunk.page,
					distance=-score,
					metadata=metadata,
				)))
		results.sort(key=lambda item: (-item[0], item[1].chunk_id))
		return [chunk for _, chunk in results[:top_k]]
class HybridRetriever:
	"""Fuse semantic and lexical rankings with Reciprocal Rank Fusion."""

	def __init__(
		self,
		semantic_retriever: Retriever,
		lexical_retriever: BM25Retriever,
		*,
		rrf_k: int = DEFAULT_RRF_K,
	) -> None:
		if rrf_k <= 0:
			raise ValueError("rrf_k must be greater than zero")
		self.semantic_retriever = semantic_retriever
		self.lexical_retriever = lexical_retriever
		self.rrf_k = rrf_k

	def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
		if not query or not query.strip():
			raise ValueError("query must not be empty")
		if top_k <= 0:
			raise ValueError("top_k must be greater than zero")
		semantic = self.semantic_retriever.retrieve(query, top_k=top_k)
		lexical = self.lexical_retriever.retrieve(query, top_k=top_k)
		by_id: dict[str, RetrievedChunk] = {}
		rrf_scores: dict[str, float] = {}
		methods: dict[str, set[str]] = {}
		for method, chunks in (("semantic", semantic), ("lexical", lexical)):
			for rank, chunk in enumerate(chunks, start=1):
				by_id.setdefault(chunk.chunk_id, chunk)
				rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + 1 / (self.rrf_k + rank)
				methods.setdefault(chunk.chunk_id, set()).add(method)
		fused: list[RetrievedChunk] = []
		for chunk_id, chunk in by_id.items():
			metadata = dict(chunk.metadata)
			metadata["retrieval_methods"] = sorted(methods[chunk_id])
			metadata["rrf_score"] = round(rrf_scores[chunk_id], 8)
			fused.append(RetrievedChunk(
				chunk_id=chunk.chunk_id,
				text=chunk.text,
				source=chunk.source,
				document_name=chunk.document_name,
				page=chunk.page,
				distance=-rrf_scores[chunk_id],
				metadata=metadata,
			))
		fused.sort(key=lambda chunk: (chunk.distance, chunk.chunk_id))
		return fused[:top_k]