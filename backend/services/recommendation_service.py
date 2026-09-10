from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ai.recommendation import recommend_cases
from backend.models.case import Case
from backend.models.donation import Donation
from backend.models.donor import Donor
from backend.schemas.case import CaseResponse


def _case_payload(case: Case) -> dict[str, Any]:
    return CaseResponse.model_validate(case).model_dump()


def _donor_payload(donor: Donor) -> dict[str, Any]:
    return {
        "donor_id": donor.donor_id,
        "preferred_category": donor.preferred_category,
        "budget": donor.budget,
        "preferred_location": donor.preferred_location,
        "urgency_preference": donor.urgency_preference,
        "previous_donations": donor.previous_donations,
    }


def _donation_payload(donation: Donation) -> dict[str, Any]:
    return {"donor_id": donation.donor_id, "case_id": donation.case_id}


def get_donor_recommendations(db: Session, donor_id: str) -> list[dict[str, Any]]:
    """Run the existing Person 2 recommender against database records."""

    clean_donor_id = (donor_id or "").strip()
    if not clean_donor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donor ID must not be empty",
        )

    donor = db.get(Donor, clean_donor_id)
    if donor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found",
        )

    cases = db.scalars(select(Case)).all()
    donations = db.scalars(select(Donation)).all()

    try:
        result = recommend_cases(
            clean_donor_id,
            cases=[_case_payload(case) for case in cases],
            donors=[_donor_payload(donor)],
            donations=[_donation_payload(donation) for donation in donations],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found",
        ) from exc

    items: list[dict[str, Any]] = []
    for recommendation in result["recommendations"]:
        item = dict(recommendation["case"])
        item["recommendation_rank"] = recommendation["rank"]
        item["recommendation_score"] = recommendation["score"]
        item["recommendation_reasons"] = recommendation["reasons"]
        item["recommendation_breakdown"] = recommendation["breakdown"]
        items.append(item)
    return items