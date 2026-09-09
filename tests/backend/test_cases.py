from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.models.user import UserRole
from backend.schemas.case import CaseCreate, CaseStatusUpdate, CaseUpdate
from backend.services import case_service


def user(user_id: str = "USER-1", role: UserRole = UserRole.USER):
    return SimpleNamespace(user_id=user_id, role=role)


def case(created_by: str | None = "USER-1"):
    return SimpleNamespace(
        case_id="CASE-TEST", description="Original", assistance_category="Food",
        people_affected=2, country="Egypt", governorate=None, city=None,
        latitude=None, longitude=None, severity="High", urgency="High",
        required_resources=None, estimated_funding=None, current_funding=0,
        submission_date=datetime.utcnow(), status="Under Review", priority=None,
        created_by=created_by,
    )


class FakeSession:
    def __init__(self, found_case=None):
        self.found_case = found_case
        self.added = None
        self.commits = 0
        self.rollbacks = 0

    def get(self, model, case_id):
        return self.found_case if self.found_case and case_id == self.found_case.case_id else None

    def add(self, value):
        self.added = value

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        return None

    def rollback(self):
        self.rollbacks += 1


class FakeListResult:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeListSession:
    def __init__(self, items):
        self.items = items
        self.count_query = None
        self.items_query = None

    def scalar(self, query):
        self.count_query = query
        return 45

    def scalars(self, query):
        self.items_query = query
        return FakeListResult(self.items)


def creation_payload(**overrides):
    values = {
        "description": "Food supplies are needed.", "assistance_category": "Food",
        "people_affected": 8, "country": "Egypt", "severity": "High", "urgency": "Critical",
    }
    values.update(overrides)
    return CaseCreate(**values)


def test_authenticated_user_can_create_case_and_server_sets_owner(monkeypatch):
    db = FakeSession()
    monkeypatch.setattr(case_service, "_new_case_id", lambda: "CASE-NEW")

    created = case_service.create_case(db, creation_payload(), user())

    assert created.case_id == "CASE-NEW"
    assert created.created_by == "USER-1"
    assert created.status == "Under Review"
    assert created.current_funding == 0
    assert db.commits == 1


def test_create_payload_cannot_set_created_by():
    with pytest.raises(Exception):
        CaseCreate(**creation_payload().model_dump(), created_by="USER-OTHER")


def test_case_validation_rejects_invalid_input():
    with pytest.raises(Exception):
        CaseCreate(
            description="", assistance_category="Food", people_affected=0,
            country="Egypt", severity="Unknown", urgency="High",
        )
    with pytest.raises(Exception):
        CaseStatusUpdate(status="Pending")


def test_get_nonexistent_case_is_404():
    with pytest.raises(HTTPException) as exc_info:
        case_service.get_case_or_404(FakeSession(), "CASE-MISSING")
    assert exc_info.value.status_code == 404


def test_list_filters_and_pagination_are_applied_by_the_query():
    db = FakeListSession([case()])

    items, total, pages = case_service.list_cases(
        db, page=2, page_size=20, country="Egypt", case_status="Active",
        assistance_category="Food",
    )

    assert items[0].case_id == "CASE-TEST"
    assert total == 45
    assert pages == 3
    compiled = str(db.items_query.compile(compile_kwargs={"literal_binds": True}))
    assert "cases.country = 'Egypt'" in compiled
    assert "cases.assistance_category = 'Food'" in compiled
    assert "cases.status = 'Active'" in compiled
    assert "LIMIT 20 OFFSET 20" in compiled


def test_user_can_update_own_case():
    stored_case = case()
    db = FakeSession(stored_case)

    updated = case_service.update_case(db, "CASE-TEST", CaseUpdate(city="Cairo"), user())

    assert updated.city == "Cairo"
    assert db.commits == 1


def test_user_cannot_update_another_users_case():
    with pytest.raises(HTTPException) as exc_info:
        case_service.update_case(
            FakeSession(case("USER-OTHER")), "CASE-TEST", CaseUpdate(city="Cairo"), user()
        )
    assert exc_info.value.status_code == 403


def test_admin_can_update_another_users_case():
    stored_case = case("USER-OTHER")
    db = FakeSession(stored_case)

    case_service.update_case(db, "CASE-TEST", CaseUpdate(city="Cairo"), user("ADMIN-1", UserRole.ADMIN))

    assert stored_case.city == "Cairo"
    assert db.commits == 1


def test_status_update_checks_owner_and_persists():
    stored_case = case()
    db = FakeSession(stored_case)

    updated = case_service.update_case_status(
        db, "CASE-TEST", CaseStatusUpdate(status="Active"), user()
    )

    assert updated.status == "Active"
    assert db.commits == 1


def test_status_update_rejects_unauthorized_user():
    with pytest.raises(HTTPException) as exc_info:
        case_service.update_case_status(
            FakeSession(case("USER-OTHER")), "CASE-TEST", CaseStatusUpdate(status="Active"), user()
        )
    assert exc_info.value.status_code == 403
