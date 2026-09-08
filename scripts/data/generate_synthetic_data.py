"""Generate deterministic, internally consistent synthetic CareHaven data.

This script uses only Python's standard library and never uses real personal data.
Run from the repository root with: python scripts/data/generate_synthetic_data.py
"""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


SEED = 20260909
CASE_COUNT = 500
DONOR_COUNT = 100
DONATION_COUNT = 1000
REFERENCE_DATE = date(2026, 9, 9)

ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "data" / "raw" / "cases" / "cases.csv"
DONORS_PATH = ROOT / "data" / "raw" / "donors" / "donors.csv"
DONATIONS_PATH = ROOT / "data" / "raw" / "donations" / "donations.csv"

CASE_COLUMNS = [
    "case_id", "description", "assistance_category", "people_affected", "country",
    "governorate", "city", "latitude", "longitude", "severity", "urgency",
    "required_resources", "estimated_funding", "current_funding", "submission_date",
    "status", "priority",
]
DONOR_COLUMNS = [
    "donor_id", "preferred_category", "budget", "preferred_location",
    "urgency_preference", "previous_donations",
]
DONATION_COLUMNS = ["donation_id", "donor_id", "case_id", "amount", "date"]

LOCATIONS = [
    ("Egypt", "Cairo", "Cairo", 30.0444, 31.2357),
    ("Egypt", "Alexandria", "Alexandria", 31.2001, 29.9187),
    ("Egypt", "Giza", "6th of October", 29.9668, 30.9262),
    ("Egypt", "Aswan", "Aswan", 24.0889, 32.8998),
    ("Jordan", "Amman", "Amman", 31.9454, 35.9284),
    ("Jordan", "Irbid", "Irbid", 32.5568, 35.8469),
    ("Lebanon", "Beirut", "Beirut", 33.8938, 35.5018),
    ("Tunisia", "Tunis", "Tunis", 36.8065, 10.1815),
]
CATEGORIES = ["Food", "Medical Aid", "Emergency Housing", "Water", "Clothing", "Education"]
LEVELS = ["Low", "Medium", "High", "Critical"]
LEVEL_SCORES = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

SCENARIOS = {
    "Food": [
        "A {people}-person household needs food parcels after {event} disrupted its income.",
        "Families affected by {event} require staple food supplies for the coming weeks.",
    ],
    "Medical Aid": [
        "Residents affected by {event} need urgent medicines, examinations, and transport to care.",
        "A family needs medical assistance after {event}, including treatment and essential supplies.",
    ],
    "Emergency Housing": [
        "A {people}-person family needs temporary shelter after {event} made their home unsafe.",
        "Housing repairs and safe temporary accommodation are needed following {event}.",
    ],
    "Water": [
        "Families need clean drinking water and storage containers after {event} affected local supplies.",
        "A community requires emergency water deliveries because {event} disrupted access to safe water.",
    ],
    "Clothing": [
        "Families need seasonal clothing, blankets, and basic hygiene items after {event}.",
        "People displaced by {event} require clothing and blankets while they recover.",
    ],
    "Education": [
        "Children need school materials and fee support after {event} interrupted household income.",
        "Education support is needed for children whose learning was disrupted by {event}.",
    ],
}
EVENTS = ["a house fire", "flash flooding", "earthquake damage", "a severe storm", "local displacement"]
RESOURCE_MAP = {
    "Food": "food parcels; cooking staples; infant nutrition",
    "Medical Aid": "medicines; clinic visits; medical transport",
    "Emergency Housing": "temporary shelter; repair materials; mattresses",
    "Water": "clean water; filtration kits; storage containers",
    "Clothing": "seasonal clothing; blankets; hygiene kits",
    "Education": "school kits; uniforms; learning materials",
}


def money(value: float) -> str:
    return f"{value:.2f}"


def random_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def make_priority(severity: str, urgency: str, people: int, funding_gap_ratio: float, category: str) -> str:
    """Turn synthetic operational factors into a label; this is not an ML model.

    Score = severity (1-4) + urgency (1-4) + affected-population band (1-3)
    + funding-gap band (0-3) + one emergency-housing/medical point. Labels are
    Critical >= 13, High >= 10, Medium >= 7, otherwise Low.
    """
    people_score = 1 if people < 10 else 2 if people < 50 else 3
    gap_score = 0 if funding_gap_ratio < 0.10 else 1 if funding_gap_ratio < 0.40 else 2 if funding_gap_ratio < 0.75 else 3
    emergency_score = 1 if category in {"Medical Aid", "Emergency Housing"} else 0
    score = LEVEL_SCORES[severity] + LEVEL_SCORES[urgency] + people_score + gap_score + emergency_score
    if score >= 13:
        return "Critical"
    if score >= 10:
        return "High"
    if score >= 7:
        return "Medium"
    return "Low"


def build_cases(rng: random.Random) -> list[dict[str, str | int | float]]:
    cases = []
    for index in range(1, CASE_COUNT + 1):
        country, governorate, city, latitude, longitude = rng.choice(LOCATIONS)
        category = rng.choice(CATEGORIES)
        severity = rng.choices(LEVELS, weights=[18, 38, 30, 14])[0]
        urgency = rng.choices(LEVELS, weights=[15, 36, 32, 17])[0]
        people = rng.randint(2, 12) if category != "Water" else rng.randint(10, 120)
        if severity in {"High", "Critical"}:
            people += rng.randint(3, 45)
        funding = round((900 + people * rng.randint(180, 520)) * (1 + 0.18 * LEVEL_SCORES[severity]), 2)
        submission_start = REFERENCE_DATE - timedelta(days=540)
        submission_date = random_date(rng, submission_start, REFERENCE_DATE - timedelta(days=1))
        event = rng.choice(EVENTS)
        description = rng.choice(SCENARIOS[category]).format(people=people, event=event)
        cases.append({
            "case_id": f"CASE-{index:04d}", "description": description,
            "assistance_category": category, "people_affected": people, "country": country,
            "governorate": governorate, "city": city, "latitude": round(latitude + rng.uniform(-0.025, 0.025), 6),
            "longitude": round(longitude + rng.uniform(-0.025, 0.025), 6), "severity": severity,
            "urgency": urgency, "required_resources": RESOURCE_MAP[category],
            "estimated_funding": funding, "submission_date": submission_date.isoformat(),
        })
    return cases


def build_donors(rng: random.Random) -> list[dict[str, str | int | float]]:
    donors = []
    locations = [f"{country} - {governorate}" for country, governorate, _, _, _ in LOCATIONS]
    for index in range(1, DONOR_COUNT + 1):
        donors.append({
            "donor_id": f"DONOR-{index:03d}", "preferred_category": rng.choice(CATEGORIES),
            "budget": round(rng.uniform(18000, 60000), 2), "preferred_location": rng.choice(locations),
            "urgency_preference": rng.choices(LEVELS, weights=[10, 30, 40, 20])[0],
            "previous_donations": rng.randint(0, 28),
        })
    return donors


def build_donations(rng: random.Random, cases: list[dict], donors: list[dict]) -> list[dict[str, str | float]]:
    remaining_case = {case["case_id"]: float(case["estimated_funding"]) for case in cases}
    remaining_donor = {donor["donor_id"]: float(donor["budget"]) for donor in donors}
    donations = []
    for index in range(1, DONATION_COUNT + 1):
        eligible_donors = [donor_id for donor_id, value in remaining_donor.items() if value >= 50]
        donor_id = rng.choice(eligible_donors)
        eligible_cases = [case for case in cases if remaining_case[case["case_id"]] >= 50]
        case = rng.choice(eligible_cases)
        case_id = case["case_id"]
        max_amount = min(2500.0, remaining_case[case_id], remaining_donor[donor_id])
        amount = round(rng.uniform(50, max_amount), 2) if max_amount >= 50 else round(max_amount, 2)
        remaining_case[case_id] -= amount
        remaining_donor[donor_id] -= amount
        received_from = date.fromisoformat(str(case["submission_date"]))
        donations.append({
            "donation_id": f"DONATION-{index:04d}", "donor_id": donor_id, "case_id": case_id,
            "amount": amount, "date": random_date(rng, received_from, REFERENCE_DATE).isoformat(),
        })
    return donations


def finalize_cases(cases: list[dict], donations: list[dict]) -> None:
    totals: defaultdict[str, float] = defaultdict(float)
    for donation in donations:
        totals[str(donation["case_id"])] += float(donation["amount"])
    for case in cases:
        current = round(totals[case["case_id"]], 2)
        estimated = float(case["estimated_funding"])
        ratio = current / estimated
        if ratio >= 0.95:
            status = "Completed" if date.fromisoformat(str(case["submission_date"])) < REFERENCE_DATE - timedelta(days=30) else "Funded"
        elif ratio >= 0.75:
            status = "Funded"
        elif date.fromisoformat(str(case["submission_date"])) > REFERENCE_DATE - timedelta(days=10) and current == 0:
            status = "Under Review"
        else:
            status = "Active"
        case["current_funding"] = current
        case["status"] = status
        case["priority"] = make_priority(case["severity"], case["urgency"], int(case["people_affected"]), 1 - ratio, case["assistance_category"])


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            formatted = {key: money(value) if key in {"estimated_funding", "current_funding", "budget", "amount"} else value for key, value in row.items()}
            writer.writerow(formatted)


def main() -> None:
    rng = random.Random(SEED)
    cases = build_cases(rng)
    donors = build_donors(rng)
    donations = build_donations(rng, cases, donors)
    finalize_cases(cases, donations)
    write_csv(CASES_PATH, CASE_COLUMNS, cases)
    write_csv(DONORS_PATH, DONOR_COLUMNS, donors)
    write_csv(DONATIONS_PATH, DONATION_COLUMNS, donations)
    print(f"Generated {len(cases)} cases, {len(donors)} donors, and {len(donations)} donations.")


if __name__ == "__main__":
    main()
