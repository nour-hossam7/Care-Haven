from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user, require_admin
from backend.models.user import User
from backend.schemas.evidence import (
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceVerificationUpdate,
)
from backend.services.case_service import get_case_or_404
from backend.services.evidence_service import (
    list_unreviewed_evidence,
    update_evidence_verification,
    upload_case_evidence,
)


router = APIRouter(prefix="/cases", tags=["Case Evidence"])


@router.get("/evidence/review-queue", response_model=EvidenceListResponse)
def get_review_queue(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    items, total, pages = list_unreviewed_evidence(
        db, page=page, page_size=page_size
    )
    return EvidenceListResponse(
        items=items, page=page, page_size=page_size, total=total, pages=pages
    )


@router.patch(
    "/evidence/{evidence_id}/verification", response_model=EvidenceResponse
)
def set_evidence_verification(
    evidence_id: str,
    payload: EvidenceVerificationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return update_evidence_verification(
        db, evidence_id, payload.verification_status
    )


@router.post(
    "/{case_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = get_case_or_404(db, case_id)

    is_admin = getattr(current_user.role, "value", current_user.role) == "admin"
    if not is_admin and case.created_by != current_user.user_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload evidence for this case",
        )

    return upload_case_evidence(
        db=db,
        case=case,
        file=file,
        description=description,
    )
