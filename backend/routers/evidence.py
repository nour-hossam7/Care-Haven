from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user, require_admin
from backend.models.user import User
from backend.schemas.evidence import (
    CaseEvidenceResponse,
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceVerificationUpdate,
)
from backend.services.case_service import get_case_or_404
from backend.services.evidence_service import (
    EVIDENCE_IMAGE_ROOT,
    is_image_evidence,
    list_case_evidence,
    list_unreviewed_evidence,
    resolve_evidence_file,
    update_evidence_verification,
    upload_case_evidence,
)


router = APIRouter(prefix="/cases", tags=["Case Evidence"])


@router.get("/evidence/files/{file_path:path}", name="get_evidence_file")
def get_evidence_file(
    file_path: str,
    _: User = Depends(get_current_user),
):
    candidate = resolve_evidence_file(str(EVIDENCE_IMAGE_ROOT / file_path))
    if candidate is None or not candidate.is_file():
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence file not found")
    return FileResponse(candidate)


@router.get("/{case_id}/evidence", response_model=list[CaseEvidenceResponse])
def get_case_evidence(
    case_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    evidence = list_case_evidence(db, case_id)
    response = []
    for item in evidence:
        image_url = None
        candidate = resolve_evidence_file(item.file_path)
        if is_image_evidence(item) and candidate is not None:
            relative_path = candidate.relative_to(EVIDENCE_IMAGE_ROOT).as_posix()
            image_url = str(
                request.url_for("get_evidence_file", file_path=relative_path)
            )
        response.append(
            CaseEvidenceResponse.model_validate(
                {**item.__dict__, "file_path": None, "image_url": image_url}
            )
        )
    return response


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
