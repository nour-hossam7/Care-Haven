"""Validate the locally generated CareHaven synthetic CSV datasets."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "data" / "raw" / "cases" / "cases.csv"
DONORS_PATH = ROOT / "data" / "raw" / "donors" / "donors.csv"
DONATIONS_PATH = ROOT / "data" / "raw" / "donations" / "donations.csv"

CASE_COLUMNS = {"case_id", "description", "assistance_category", "people_affected", "country", "governorate", "city", "latitude", "longitude", "severity", "urgency", "required_resources", "estimated_funding", "current_funding", "submission_date", "status", "priority"}
DONOR_COLUMNS = {"donor_id", "preferred_category", "budget", "preferred_location", "urgency_preference", "previous_donations"}
DONATION_COLUMNS = {"donation_id", "donor_id", "case_id", "amount", "date"}
CATEGORIES = {"Food", "Medical Aid", "Emergency Housing", "Water", "Clothing", "Education"}
LEVELS = {"Low", "Medium", "High", "Critical"}
STATUSES = {"Active", "Under Review", "Funded", "Completed"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as input_file:
        return list(csv.DictReader(input_file))


def is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate() -> list[str]:
    errors: list[str] = []
    for path in (CASES_PATH, DONORS_PATH, DONATIONS_PATH):
        if not path.exists():
            errors.append(f"Missing dataset: {path.relative_to(ROOT)}")
    if errors:
        return errors

    cases, donors, donations = read_csv(CASES_PATH), read_csv(DONORS_PATH), read_csv(DONATIONS_PATH)
    if not cases or not donors or not donations:
        errors.append("Datasets must not be empty.")
        return errors
    if set(cases[0]) != CASE_COLUMNS: errors.append("Cases required columns do not match schema.")
    if set(donors[0]) != DONOR_COLUMNS: errors.append("Donors required columns do not match schema.")
    if set(donations[0]) != DONATION_COLUMNS: errors.append("Donations required columns do not match schema.")
    if errors:
        return errors

    def duplicate_ids(rows: list[dict[str, str]], field: str) -> bool:
        values = [row[field] for row in rows]
        return len(values) != len(set(values))

    for rows, field, label in ((cases, "case_id", "case"), (donors, "donor_id", "donor"), (donations, "donation_id", "donation")):
        if duplicate_ids(rows, field): errors.append(f"Duplicate {label} IDs found.")
        if any(not value.strip() for row in rows for value in row.values()): errors.append(f"Missing required value in {label} data.")

    for row in cases:
        try:
            people, estimated, current = int(row["people_affected"]), float(row["estimated_funding"]), float(row["current_funding"])
            latitude, longitude = float(row["latitude"]), float(row["longitude"])
            if people <= 0: errors.append(f"{row['case_id']}: people_affected must be positive.")
            if estimated <= 0: errors.append(f"{row['case_id']}: estimated_funding must be positive.")
            if not 0 <= current <= estimated: errors.append(f"{row['case_id']}: invalid current_funding.")
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180: errors.append(f"{row['case_id']}: invalid coordinates.")
        except ValueError: errors.append(f"{row['case_id']}: invalid numeric type.")
        if row["assistance_category"] not in CATEGORIES: errors.append(f"{row['case_id']}: invalid category.")
        if any(row[field] not in LEVELS for field in ("severity", "urgency", "priority")): errors.append(f"{row['case_id']}: invalid level.")
        if row["status"] not in STATUSES: errors.append(f"{row['case_id']}: invalid status.")
        if not is_date(row["submission_date"]): errors.append(f"{row['case_id']}: invalid submission date.")

    donor_ids, case_ids = {row["donor_id"] for row in donors}, {row["case_id"] for row in cases}
    case_submission_dates = {row["case_id"]: row["submission_date"] for row in cases}
    case_totals = {case_id: 0.0 for case_id in case_ids}
    for row in donors:
        try:
            if float(row["budget"]) <= 0 or int(row["previous_donations"]) < 0: errors.append(f"{row['donor_id']}: invalid donor numeric value.")
        except ValueError: errors.append(f"{row['donor_id']}: invalid donor numeric type.")
        if row["preferred_category"] not in CATEGORIES or row["urgency_preference"] not in LEVELS: errors.append(f"{row['donor_id']}: invalid donor category or urgency.")
    for row in donations:
        try:
            amount = float(row["amount"])
            if amount <= 0: errors.append(f"{row['donation_id']}: amount must be positive.")
            case_totals[row["case_id"]] = case_totals.get(row["case_id"], 0) + amount
        except ValueError: errors.append(f"{row['donation_id']}: invalid donation amount.")
        if row["donor_id"] not in donor_ids: errors.append(f"{row['donation_id']}: unknown donor.")
        if row["case_id"] not in case_ids: errors.append(f"{row['donation_id']}: unknown case.")
        if not is_date(row["date"]): errors.append(f"{row['donation_id']}: invalid donation date.")
        elif row["case_id"] in case_submission_dates and row["date"] < case_submission_dates[row["case_id"]]:
            errors.append(f"{row['donation_id']}: donation predates its case submission.")
    for row in cases:
        if round(case_totals[row["case_id"]], 2) != round(float(row["current_funding"]), 2): errors.append(f"{row['case_id']}: current_funding does not equal donations.")
    return errors


def main() -> None:
    errors = validate()
    print("CareHaven Data Validation\n-------------------------")
    labels = ["Cases", "Donors", "Donations", "Relationships", "Missing Values", "Value Ranges"]
    for label in labels:
        print(f"{label}: {'PASS' if not errors else 'FAIL'}")
    if errors:
        print("\nErrors:")
        for error in errors[:20]: print(f"- {error}")
        print("\nOverall Status: FAIL")
        raise SystemExit(1)
    print("\nOverall Status: PASS")


if __name__ == "__main__":
    main()
