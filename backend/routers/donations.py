from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.schemas.donation import DonationCreate, DonationListResponse, DonationResponse
from backend.services.donation_service import (
    create_donation,
    get_case_donations,
    get_donation,
    get_my_donations,
    list_donations,
)


router = APIRouter(prefix="/donations", tags=["Donations"])
case_donations_router = APIRouter(prefix="/cases", tags=["Donations"])


@router.post("", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_donation(db, payload, current_user)


@router.get("/my-history", response_model=DonationListResponse)
def my_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, pages = get_my_donations(db, current_user, page, page_size)
    return DonationListResponse(items=items, page=page, page_size=page_size, total=total, pages=pages)


@router.get("", response_model=DonationListResponse)
def list_all(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, pages = list_donations(db, current_user, page, page_size)
    return DonationListResponse(items=items, page=page, page_size=page_size, total=total, pages=pages)


@router.get("/{donation_id}", response_model=DonationResponse)
def get_one(
    donation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_donation(db, donation_id, current_user)


@case_donations_router.get("/{case_id}/donations", response_model=DonationListResponse)
def list_for_case(
    case_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, pages = get_case_donations(db, case_id, current_user, page, page_size)
    return DonationListResponse(items=items, page=page, page_size=page_size, total=total, pages=pages)
