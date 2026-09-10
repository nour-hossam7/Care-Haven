from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from math import ceil
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ai.vision.preprocessing import load_image
from ai.vision.quality import assess_image_quality
from backend.models.case import Case
from backend.models.case_image import CaseEvidence


UPLOAD_DIR = Path("data/raw/images/uploads")
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
REVIEWABLE_STATUSES = {"unreviewed", "approved", "rejected"}


def upload_case_evidence(
    db: Session,
    case: Case,
    file: UploadFile,
    description: str | None = None,
) -> CaseEvidence:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Use JPG, PNG, or WEBP.",
        )

    content = file.file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image file is too large. Maximum size is 10 MB.",
        )

    try:
        _image = load_image(content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    quality = assess_image_quality(content)

    if not quality["is_acceptable"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Image quality is not acceptable.",
                "quality": quality,
            },
        )

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    evidence_id = f"EVIDENCE-{uuid4().hex.upper()}"
    filename = f"{evidence_id}{extension}"

    upload_dir = UPLOAD_DIR / case.case_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    file_path.write_bytes(content)

    evidence = CaseEvidence(
        evidence_id=evidence_id,
        case_id=case.case_id,
        evidence_type="image",
        file_path=str(file_path),
        source_type="user_upload",
        uploaded_at=datetime.utcnow(),
        description=description,
        verification_status="unreviewed",
    )

    try:
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
    except Exception as exc:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save uploaded evidence.",
        ) from exc

    return evidence


def list_unreviewed_evidence(
    db: Session, *, page: int, page_size: int
) -> tuple[list[CaseEvidence], int, int]:
    """Return pending image evidence in a stable, paginated review queue."""
    query = select(CaseEvidence).where(
        CaseEvidence.verification_status == "unreviewed"
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(CaseEvidence.uploaded_at, CaseEvidence.evidence_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return items, total, ceil(total / page_size) if total else 0


def update_evidence_verification(
    db: Session, evidence_id: str, verification_status: str
) -> CaseEvidence:
    """Set an evidence review decision without altering its file or metadata."""
    if verification_status not in REVIEWABLE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid verification status.",
        )

    evidence = db.get(CaseEvidence, evidence_id)
    if evidence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        )

    evidence.verification_status = verification_status
    try:
        db.commit()
        db.refresh(evidence)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update evidence verification status.",
        ) from exc
    return evidence
