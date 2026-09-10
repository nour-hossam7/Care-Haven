from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.case import Case
from backend.models.donor import Donor
from backend.services import recommendation_service


def donor(donor_id: str = "DONOR-001"):
    return SimpleNamespace(
        donor_id=donor_id,
        preferred_category="Food",
        budget=1000,
        preferred_location="Egypt - Cairo",
        urgency_preference="High",
        previous_donations=1,
    )


def case(case_id: str = "CASE-1", status: str = "Active"):
    return SimpleNamespace(
        case_id=case_id,
        description="Food supplies needed",
        assistance_category="Food",
        people_affected=5,
        country="Egypt",
        governorate="Cairo",
        city="Cairo",
        latitude=30.04,
        longitude=31.23,
        severity="High",
        urgency="High",
        required_resources="Food boxes",
        estimated_funding=2000,
        current_funding=500,
        submission_date=datetime.utcnow(),
        status=status,
        priority="High",
        created_by="USER-1",
    )


def donation(donor_id: str = "DONOR-001", case_id: str = "CASE-1"):
    return SimpleNamespace(donor_id=donor_id, case_id=case_id)


class FakeScalars:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeSession:
    def __init__(self, donor_row=None, cases=None, donations=None):
        self.donor_row = donor_row
        self.cases = cases or []
        self.donations = donations or []

    def get(self, model, donor_id):
        if model is Donor and self.donor_row and self.donor_row.donor_id == donor_id:
            return self.donor_row
        return None

    def scalars(self, query):
        if str(query).startswith("SELECT cases"):
            return FakeScalars(self.cases)
        return FakeScalars(self.donations)


def test_recommendation_service_ranks_eligible_cases_for_existing_donor():
    db = FakeSession(
        donor_row=donor(),
        cases=[case(status="Active"), case(case_id="CASE-FUNDED", status="Funded")],
        donations=[donation()],
    )

    items = recommendation_service.get_donor_recommendations(db, "DONOR-001")

    assert items, "expected at least one recommendation"
    assert items[0]["case_id"] == "CASE-1"
    assert items[0]["recommendation_rank"] == 1
    assert 0.0 <= items[0]["recommendation_score"] <= 1.0
    assert isinstance(items[0]["recommendation_reasons"], list)
    assert isinstance(items[0]["recommendation_breakdown"], dict)
    assert items[0]["status"] == "Active"


def test_recommendation_service_unknown_donor_is_404():
    with pytest.raises(HTTPException) as exc_info:
        recommendation_service.get_donor_recommendations(FakeSession(), "DONOR-MISSING")
    assert exc_info.value.status_code == 404


def test_recommendation_service_empty_donor_id_is_400():
    with pytest.raises(HTTPException) as exc_info:
        recommendation_service.get_donor_recommendations(FakeSession(), "   ")
    assert exc_info.value.status_code == 400


def test_recommendation_service_returns_empty_list_with_no_eligible_cases():
    db = FakeSession(
        donor_row=donor(),
        cases=[case(status="Funded")],
        donations=[],
    )

    items = recommendation_service.get_donor_recommendations(db, "DONOR-001")

    assert items == []


def test_recommendation_endpoint_requires_authentication():
    response = TestClient(app).get("/recommendations/DONOR-001")
    assert response.status_code == 401