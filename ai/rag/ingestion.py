"""Discovery, extraction, and light cleaning for trusted RAG documents."""

from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)
SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}
DEFAULT_DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "documents" / "rag"


class DocumentIngestionError(RuntimeError):
	"""Raised when a supported source document cannot be read or parsed."""


@dataclass(frozen=True)
class SourcePage:
	"""Clean text extracted from one source document page or text file."""

	text: str
	source: str
	source_path: str
	document_name: str
	file_type: str
	page: int | None = None
	metadata: dict[str, Any] = field(default_factory=dict)


def clean_text(text: str) -> str:
	"""Normalize extraction noise while retaining paragraphs and punctuation."""

	normalized = text.replace("\u00ad", "").replace("\u00a0", " ")
	normalized = re.sub(r"(?<!\n)-\n(?=\w)", "", normalized)
	normalized = re.sub(r"[ \t]+", " ", normalized)
	normalized = re.sub(r"\n[ \t]+", "\n", normalized)
	normalized = re.sub(r"\n{3,}", "\n\n", normalized)
	return normalized.strip()


def _metadata_by_path(directory: Path) -> dict[str, dict[str, str]]:
	metadata_path = directory / "metadata.csv"
	if not metadata_path.is_file():
		return {}
	with metadata_path.open(encoding="utf-8", newline="") as handle:
		rows = csv.DictReader(handle)
		result: dict[str, dict[str, str]] = {}
		for row in rows:
			local_file = row.get("local_file", "")
			if local_file:
				result[Path(local_file).name] = {key: value for key, value in row.items() if value}
		return result


class DocumentIngestor:
	"""Discover and extract trusted humanitarian source documents."""

	def __init__(self, documents_dir: str | Path | None = None) -> None:
		self.documents_dir = Path(documents_dir or DEFAULT_DOCUMENTS_DIR).resolve()
		self._metadata = _metadata_by_path(self.documents_dir) if self.documents_dir.is_dir() else {}

	def discover_documents(self) -> list[Path]:
		"""Return supported documents in deterministic path order."""

		if not self.documents_dir.exists():
			raise DocumentIngestionError(f"RAG documents directory does not exist: {self.documents_dir}")
		if not self.documents_dir.is_dir():
			raise DocumentIngestionError(f"RAG documents path is not a directory: {self.documents_dir}")
		return sorted(
			(path for path in self.documents_dir.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES),
			key=lambda path: path.name.lower(),
		)

	def ingest_document(self, path: str | Path) -> list[SourcePage]:
		"""Extract one supported document into page-aware source records."""

		document_path = Path(path).resolve()
		if not document_path.is_file():
			raise DocumentIngestionError(f"RAG source document does not exist: {document_path}")
		suffix = document_path.suffix.lower()
		if suffix not in SUPPORTED_SUFFIXES:
			raise DocumentIngestionError(f"Unsupported RAG document type: {document_path.name}")

		try:
			raw_pages = self._extract_pdf(document_path) if suffix == ".pdf" else [(None, document_path.read_text(encoding="utf-8"))]
		except Exception as exc:
			raise DocumentIngestionError(f"Could not read RAG document {document_path}: {exc}") from exc

		document_metadata = self._metadata.get(document_path.name, {})
		source = document_metadata.get("source", document_path.as_posix())
		pages: list[SourcePage] = []
		timestamp = datetime.now(timezone.utc).isoformat()
		for page_number, raw_text in raw_pages:
			text = clean_text(raw_text)
			if not text:
				LOGGER.warning("Skipping empty page %s in %s", page_number, document_path.name)
				continue
			metadata: dict[str, Any] = dict(document_metadata)
			metadata.update({"ingested_at": timestamp, "file_type": suffix.lstrip(".")})
			pages.append(
				SourcePage(
					text=text,
					source=source,
					source_path=document_path.as_posix(),
					document_name=document_path.name,
					file_type=suffix.lstrip("."),
					page=page_number,
					metadata=metadata,
				)
			)
		if not pages:
			raise DocumentIngestionError(f"RAG document contains no readable text: {document_path}")
		LOGGER.info("Ingested %s page(s) from %s", len(pages), document_path.name)
		return pages

	def ingest_all(self, *, strict: bool = True) -> list[SourcePage]:
		"""Extract every supported source, optionally continuing past bad files."""

		pages: list[SourcePage] = []
		for path in self.discover_documents():
			try:
				pages.extend(self.ingest_document(path))
			except DocumentIngestionError:
				if strict:
					raise
				LOGGER.exception("Skipping unreadable RAG source: %s", path)
		if not pages:
			raise DocumentIngestionError(f"No readable RAG documents found in {self.documents_dir}")
		return pages

	@staticmethod
	def _extract_pdf(path: Path) -> Iterable[tuple[int, str]]:
		try:
			from pypdf import PdfReader
		except ImportError as exc:
			raise DocumentIngestionError("PDF ingestion requires the 'pypdf' package") from exc
		reader = PdfReader(str(path))
		for index, page in enumerate(reader.pages, start=1):
			yield index, page.extract_text() or ""
