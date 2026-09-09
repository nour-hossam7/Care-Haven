from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.schemas.case import (
    CaseCreate,
    CaseListResponse,
    CaseResponse,
    CaseStatusUpdate,
    CaseUpdate,
)
from backend.services.case_service import (
    create_case,
    get_case_or_404,
    list_cases,
    update_case,
    update_case_status,
)


router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_case(db, payload, current_user)


@router.get("", response_model=CaseListResponse)
def list_all(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    assistance_category: str | None = None,
    country: str | None = None,
    governorate: str | None = None,
    city: str | None = None,
    priority: str | None = None,
    severity: str | None = None,
    urgency: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, pages = list_cases(
        db, page=page, page_size=page_size, assistance_category=assistance_category,
        country=country, governorate=governorate, city=city, priority=priority,
        severity=severity, urgency=urgency, case_status=status_filter,
    )
    return CaseListResponse(items=items, page=page, page_size=page_size, total=total, pages=pages)


@router.get("/{case_id}", response_model=CaseResponse)
def get_one(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_case_or_404(db, case_id)


@router.put("/{case_id}", response_model=CaseResponse)
def update(
    case_id: str,
    payload: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_case(db, case_id, payload, current_user)


@router.patch("/{case_id}/status", response_model=CaseResponse)
def update_status(
    case_id: str,
    payload: CaseStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_case_status(db, case_id, payload, current_user)
