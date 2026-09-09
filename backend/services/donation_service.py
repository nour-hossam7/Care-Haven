from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from math import ceil
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.case import Case
from backend.models.donation import Donation
from backend.models.user import User
from backend.schemas.donation import DonationCreate


def _is_admin(user: User) -> bool:
    return getattr(user.role, "value", user.role) == "admin"


def _new_donation_id() -> str:
    return f"DONATION-{uuid4().hex.upper()}"


def _as_decimal(value: object | None, *, stored: bool = False) -> Decimal:
    """Read the numeric JSON representation without doing float arithmetic."""
    if value is None:
        return Decimal("0")
    error_status = status.HTTP_500_INTERNAL_SERVER_ERROR if stored else status.HTTP_400_BAD_REQUEST
    error_detail = "Invalid stored funding value" if stored else "Donation amount must be a positive number"
    if isinstance(value, bool):
        raise HTTPException(status_code=error_status, detail=error_detail)
    if not isinstance(value, (int, float, str, Decimal)):
        raise HTTPException(status_code=error_status, detail=error_detail)
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid stored funding value") from exc
    if not amount.is_finite():
        raise HTTPException(status_code=error_status, detail=error_detail)
    return amount


def _invalid_amount() -> Decimal:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Donation amount must be a positive number")


def _json_number(value: Decimal, existing: object | None) -> int | float:
    """Keep integer funding integer; otherwise retain the dataset's JSON number style."""
    if isinstance(existing, int) and not isinstance(existing, bool) and value == value.to_integral_value():
        return int(value)
    if existing is None and value == value.to_integral_value():
        return int(value)
    return float(value)


def get_case_or_404(db: Session, case_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def get_donation_or_404(db: Session, donation_id: str) -> Donation:
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found")
    return donation


def create_donation(db: Session, payload: DonationCreate, current_user: User) -> Donation:
    case = get_case_or_404(db, payload.case_id)
    amount = _as_decimal(payload.amount)
    if amount <= 0:
        _invalid_amount()

    previous_funding = case.current_funding
    updated_funding = _as_decimal(previous_funding, stored=True) + amount
    donation = Donation(
        donation_id=_new_donation_id(),
        case_id=case.case_id,
        user_id=current_user.user_id,
        donor_id=None,
        amount=_json_number(amount, None),
        # The Neon column is timezone-naive, so persist the UTC instant without tzinfo.
        date=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    case.current_funding = _json_number(updated_funding, previous_funding)

    try:
        db.add(donation)
        db.commit()
        db.refresh(donation)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create donation",
        ) from exc
    return donation


def _paginate(query, db: Session, page: int, page_size: int) -> tuple[list[Donation], int, int]:
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Donation.date.desc(), Donation.donation_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return items, total, ceil(total / page_size) if total else 0


def list_donations(db: Session, current_user: User, page: int, page_size: int) -> tuple[list[Donation], int, int]:
    query = select(Donation)
    if not _is_admin(current_user):
        query = query.where(Donation.user_id == current_user.user_id)
    return _paginate(query, db, page, page_size)


def get_donation(db: Session, donation_id: str, current_user: User) -> Donation:
    donation = get_donation_or_404(db, donation_id)
    if not _is_admin(current_user) and donation.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this donation")
    return donation


def get_my_donations(db: Session, current_user: User, page: int, page_size: int) -> tuple[list[Donation], int, int]:
    return _paginate(select(Donation).where(Donation.user_id == current_user.user_id), db, page, page_size)


def get_case_donations(
    db: Session, case_id: str, current_user: User, page: int, page_size: int
) -> tuple[list[Donation | dict[str, object]], int, int]:
    get_case_or_404(db, case_id)
    items, total, pages = _paginate(select(Donation).where(Donation.case_id == case_id), db, page, page_size)
    if _is_admin(current_user):
        return items, total, pages
    # Case listings do not disclose other application users or legacy donor identifiers.
    return [
        {
            "donation_id": item.donation_id,
            "case_id": item.case_id,
            "user_id": item.user_id if item.user_id == current_user.user_id else None,
            "donor_id": None,
            "amount": item.amount,
            "date": item.date,
        }
        for item in items
    ], total, pages
