"""Run retrieval questions against the trusted CareHaven RAG corpus.

Indexing and generation require the optional Person 2 dependencies and a local
Ollama model. Retrieval remains independently testable through the RAG API.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.rag import RAGPipeline
from ai.rag.embeddings import EmbeddingError
from ai.rag.vector_store import VectorStoreError

QUESTIONS = [
    "What is emergency needs assessment?",
    "What should be considered when assessing humanitarian needs?",
    "What information is useful for planning an emergency response?",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", action="store_true", help="Build or update the persistent knowledge index first.")
    parser.add_argument("--question", action="append", help="Question to retrieve; may be supplied more than once.")
    parser.add_argument("--generate", action="store_true", help="Also call Ollama for grounded answers.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    pipeline = RAGPipeline()
    try:
        if args.index:
            print(pipeline.build_index())
        questions = args.question or QUESTIONS
        for question in questions:
            chunks = pipeline.retrieve(question)
            print(f"\nQUESTION:\n{question}\n\nRETRIEVED CHUNKS: {len(chunks)}")
            for index, chunk in enumerate(chunks, start=1):
                print(f"{index}. {chunk.document_name} page={chunk.page} distance={chunk.distance:.4f}")
                print(f"   {chunk.text[:240].replace(chr(10), ' ')}")
            if args.generate:
                response = pipeline.ask(question)
                print(f"ANSWER:\n{response.answer or response.error}")
                print(f"SOURCES:\n{response.sources}")
        return 0
    except (EmbeddingError, VectorStoreError, ValueError) as exc:
        print(f"RAG demo could not run: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
