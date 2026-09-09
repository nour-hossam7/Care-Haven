from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.models.user import UserRole
from backend.schemas.donation import DonationCreate
from backend.services import donation_service


def user(user_id: str = "USER-1", role: UserRole = UserRole.USER):
    return SimpleNamespace(user_id=user_id, role=role)


def case(current_funding=1000):
    return SimpleNamespace(case_id="CASE-TEST", current_funding=current_funding)


def donation(user_id="USER-1"):
    return SimpleNamespace(
        donation_id="DONATION-TEST", case_id="CASE-TEST", user_id=user_id,
        donor_id=None, amount=25.5, date=datetime.now(),
    )


class FakeSession:
    def __init__(self, found_case=None, found_donation=None, fail_commit=False):
        self.found_case = found_case
        self.found_donation = found_donation
        self.fail_commit = fail_commit
        self.added = None
        self.commits = 0
        self.rollbacks = 0

    def get(self, model, identifier):
        if self.found_case and identifier == self.found_case.case_id:
            return self.found_case
        if self.found_donation and identifier == self.found_donation.donation_id:
            return self.found_donation
        return None

    def add(self, value):
        self.added = value

    def commit(self):
        self.commits += 1
        if self.fail_commit:
            raise RuntimeError("database failure")

    def refresh(self, value):
        return None

    def rollback(self):
        self.rollbacks += 1


def payload(**overrides):
    values = {"case_id": "CASE-TEST", "amount": "25.50"}
    values.update(overrides)
    return DonationCreate(**values)


def test_authenticated_user_donation_sets_user_and_updates_funding(monkeypatch):
    db = FakeSession(found_case=case())
    monkeypatch.setattr(donation_service, "_new_donation_id", lambda: "DONATION-NEW")

    created = donation_service.create_donation(db, payload(), user())

    assert created.donation_id == "DONATION-NEW"
    assert created.user_id == "USER-1"
    assert created.donor_id is None
    assert created.case_id == "CASE-TEST"
    assert db.found_case.current_funding == 1025.5
    assert db.commits == 1


def test_donation_payload_forbids_impersonation_and_server_fields():
    with pytest.raises(Exception):
        DonationCreate(case_id="CASE-TEST", amount="1", user_id="USER-OTHER")
    with pytest.raises(Exception):
        DonationCreate(case_id="CASE-TEST", amount="1", donor_id="DONOR-1")


@pytest.mark.parametrize("amount", ["0", "-1"])
def test_zero_or_negative_donations_are_rejected(amount):
    with pytest.raises(Exception):
        payload(amount=amount)


def test_nonexistent_case_is_404():
    with pytest.raises(HTTPException) as exc_info:
        donation_service.create_donation(FakeSession(), payload(), user())
    assert exc_info.value.status_code == 404


def test_write_failure_rolls_back_donation_and_funding_transaction():
    stored_case = case()
    db = FakeSession(found_case=stored_case, fail_commit=True)

    with pytest.raises(HTTPException) as exc_info:
        donation_service.create_donation(db, payload(), user())

    assert exc_info.value.status_code == 500
    assert db.rollbacks == 1
    assert db.commits == 1


def test_user_can_retrieve_own_donation():
    found = donation()
    assert donation_service.get_donation(FakeSession(found_donation=found), found.donation_id, user()) is found


def test_user_cannot_retrieve_another_users_donation():
    with pytest.raises(HTTPException) as exc_info:
        donation_service.get_donation(FakeSession(found_donation=donation("USER-OTHER")), "DONATION-TEST", user())
    assert exc_info.value.status_code == 403


def test_admin_can_retrieve_any_donation():
    found = donation("USER-OTHER")
    assert donation_service.get_donation(
        FakeSession(found_donation=found), found.donation_id, user("ADMIN-1", UserRole.ADMIN)
    ) is found


def test_nonexistent_donation_is_404():
    with pytest.raises(HTTPException) as exc_info:
        donation_service.get_donation(FakeSession(), "DONATION-MISSING", user())
    assert exc_info.value.status_code == 404
