from __future__ import annotations

from datetime import datetime
from math import ceil
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.case import Case
from backend.models.user import User
from backend.schemas.case import CaseCreate, CaseStatusUpdate, CaseUpdate


def _is_admin(user: User) -> bool:
    return getattr(user.role, "value", user.role) == "admin"


def _new_case_id() -> str:
    """Produce a collision-resistant ID without relying on a table counter."""
    return f"CASE-{uuid4().hex.upper()}"


def get_case_or_404(db: Session, case_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def create_case(db: Session, payload: CaseCreate, current_user: User) -> Case:
    case = Case(
        case_id=_new_case_id(),
        **payload.model_dump(),
        current_funding=0,
        submission_date=datetime.utcnow(),
        status="Under Review",
        created_by=current_user.user_id,
    )
    try:
        db.add(case)
        db.commit()
        db.refresh(case)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create case",
        ) from exc
    return case


def list_cases(
    db: Session,
    *,
    page: int,
    page_size: int,
    assistance_category: str | None = None,
    country: str | None = None,
    governorate: str | None = None,
    city: str | None = None,
    priority: str | None = None,
    severity: str | None = None,
    urgency: str | None = None,
    case_status: str | None = None,
) -> tuple[list[Case], int, int]:
    query = select(Case)
    filters = {
        "assistance_category": assistance_category,
        "country": country,
        "governorate": governorate,
        "city": city,
        "priority": priority,
        "severity": severity,
        "urgency": urgency,
        "status": case_status,
    }
    for field, value in filters.items():
        if value is not None:
            query = query.where(getattr(Case, field) == value)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Case.submission_date.desc(), Case.case_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return items, total, ceil(total / page_size) if total else 0


def _assert_can_modify(case: Case, current_user: User) -> None:
    if _is_admin(current_user):
        return
    if case.created_by != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this case")


def update_case(db: Session, case_id: str, payload: CaseUpdate, current_user: User) -> Case:
    case = get_case_or_404(db, case_id)
    _assert_can_modify(case, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    try:
        db.commit()
        db.refresh(case)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to update case") from exc
    return case


def update_case_status(
    db: Session, case_id: str, payload: CaseStatusUpdate, current_user: User
) -> Case:
    case = get_case_or_404(db, case_id)
    _assert_can_modify(case, current_user)
    case.status = payload.status
    try:
        db.commit()
        db.refresh(case)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to update case status") from exc
    return case
