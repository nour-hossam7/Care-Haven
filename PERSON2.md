# CareHaven Person 2

## Scope

Person 2 provides RAG, donor-to-case recommendation, and anomaly-review signals. These modules accept plain mappings and do not require FastAPI or database access.

## RAG

The RAG flow is:

```text
IFRC PDF -> ingestion -> deterministic chunks -> Sentence Transformers -> ChromaDB
                                                     \-> local BM25 lexical index
semantic results + lexical results -> Reciprocal Rank Fusion -> top-k chunks -> Ollama
```

The embedding model is `sentence-transformers/all-MiniLM-L6-v2`. Chroma persists under `data/rag_documents/chroma/` in the `carehaven_humanitarian_knowledge` collection. Ollama defaults are `OLLAMA_BASE_URL=http://localhost:11434` and `OLLAMA_MODEL=qwen3:4b`.

Build or update the existing local index from the repository root:

```powershell
python scripts/rag_demo.py --index
```

Run retrieval or grounded generation:

```powershell
python scripts/rag_demo.py --question "What is emergency needs assessment?"
python scripts/rag_demo.py --generate --question "What is emergency needs assessment?"
```

Public interfaces:

- `RAGPipeline.retrieve(question, top_k=None)` performs existing semantic retrieval.
- `RAGPipeline.hybrid_retrieve(question, top_k=None)` combines semantic and BM25 results with deterministic Reciprocal Rank Fusion.
- `RAGPipeline.ask(question)` performs the existing semantic retrieval plus grounded Ollama generation.
- `RAGPipeline.ask_hybrid(question, top_k=None)` performs fused retrieval plus grounded Ollama generation.
- `BM25Retriever` provides local lexical retrieval over `RetrievedChunk` records.
- `HybridRetriever` accepts a semantic retriever and lexical retriever and returns deduplicated `RetrievedChunk` records with `retrieval_methods` and `rrf_score` metadata.

Hybrid retrieval works when either source is empty and returns an empty list for an empty corpus. It does not add a second vector database, embedding model, or LLM.

## Recommendation

`recommend_cases(donor_id, cases, donors, donations=None, top_n=5, weights=None)` returns deterministic serialized recommendations. The default weights are category 30%, location 25%, priority 20%, funding need 15%, and donor behavior 10%. Lower-level `match_donor_to_cases()` and `rank_candidates()` are also available.

## Anomaly Review

- `detect_anomalies(records, entity_type="donation"|"case", ...)` uses deterministic Isolation Forest review signals.
- `detect_similar_cases(cases, threshold=...)` detects exact and TF-IDF-similar descriptions.
- `analyze_dataset(cases, donations, donors=None, ...)` returns a JSON-safe combined report.

Outputs recommend human review and do not label people or records fraudulent.

## Tests and Integration

Run Person 2 tests:

```powershell
python -m pytest tests/rag -q
python -m pytest tests/recommendation -q
python -m pytest tests/anomaly -q
```

Person 1-C should convert ORM rows into mappings before calling recommendation or anomaly functions. RAG requires the existing IFRC corpus to be indexed locally and requires Ollama only for generation, not retrieval tests.