from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.case import Case
from backend.models.donor import Donor
from backend.services.recommendation_service import get_donor_recommendations

LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
CATEGORIES = ("food", "medical aid", "emergency housing", "water", "clothing", "education")
LIVE_TERMS = (
    "case", "cases", "funding", "urgent", "priority", "critical", "donor",
    "recommend", "suitable", "cairo", "education", "people affected", "needs assistance",
)


def is_live_question(question: str) -> bool:
    text = question.casefold()
    return any(re.search(rf"\b{re.escape(term)}\b", text) for term in LIVE_TERMS)


def is_mixed_question(question: str) -> bool:
    text = question.casefold()
    return is_live_question(question) and bool(
        re.search(r"\b(?:why|how|should|consider|explain)\b", text)
    )


def _limit(question: str, default: int = 5) -> int:
    if re.search(r"\b(?:top|show|recommend|find)\s+one\b", question.casefold()):
        return 1
    match = re.search(r"\b(?:top|show|recommend|find)\s+(\d+)\b", question.casefold())
    return max(1, min(int(match.group(1)), 20)) if match else default


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _gap(case: Case) -> float:
    return max(_number(case.estimated_funding) - _number(case.current_funding), 0.0)


def _matches(case: Case, question: str) -> bool:
    text = question.casefold()
    searchable = " ".join(
        str(value or "")
        for value in (case.country, case.governorate, case.city, case.assistance_category)
    ).casefold()
    return not any(term in text for term in ("cairo", "education", "food", "water", "medical")) or any(
        term in searchable for term in ("cairo", "education", "food", "water", "medical") if term in text
    )


def _filter_cases(cases: Iterable[Case], question: str) -> list[Case]:
    text = question.casefold()
    result = [case for case in cases if case.status and case.status.casefold() in {"active", "under review"}]
    location_values = {
        str(value).casefold()
        for case in result
        for value in (case.country, case.governorate, case.city)
        if value and len(str(value).strip()) > 2
    }
    requested_locations = [value for value in location_values if value in text]
    if requested_locations:
        result = [
            case for case in result
            if any(
                location in " ".join(str(value or "").casefold() for value in (case.country, case.governorate, case.city))
                for location in requested_locations
            )
        ]
    elif re.search(r"\b(?:in|from)\s+[a-z][a-z ]+", text):
        result = []
    category = next((value for value in CATEGORIES if value in text), None)
    if category:
        result = [case for case in result if (case.assistance_category or "").casefold() == category]
    if "critical" in text:
        result = [case for case in result if (case.priority or "").casefold() == "critical"]
    elif "high-priority" in text or "highest-priority" in text or "high priority" in text:
        result = [case for case in result if (case.priority or "").casefold() in {"high", "critical"}]
    if any(term in text for term in ("funding gap", "still need funding", "need funding")):
        result = [case for case in result if _gap(case) > 0]
    if any(term in text for term in ("urgent", "immediate")):
        result = [case for case in result if (case.urgency or "").casefold() in {"high", "critical"}]
    return result


def _format_cases(cases: list[Case], heading: str) -> str:
    if not cases:
        return "No matching cases were found in the live CareHaven database."
    lines = [heading]
    for index, case in enumerate(cases, 1):
        location = ", ".join(str(value) for value in (case.city, case.governorate, case.country) if value)
        lines.extend(
            [
                f"{index}. {case.case_id}",
                f"   Location: {location or 'Not specified'}",
                f"   Priority: {case.priority or 'Not specified'} | Severity: {case.severity or 'Not specified'} | Urgency: {case.urgency or 'Not specified'}",
                f"   People affected: {case.people_affected if case.people_affected is not None else 'Not specified'}",
                f"   Funding gap: {_gap(case):,.2f}",
                f"   Need: {case.assistance_category or 'Not specified'}; {case.required_resources or 'Not specified'}",
            ]
        )
    return "\n".join(lines)


def _recommend_cases(db: Session, question: str, limit: int) -> str:
    text = question.casefold()
    category = next((value for value in CATEGORIES if value in text), None)
    donors = db.scalars(select(Donor)).all()
    if category:
        donors = [donor for donor in donors if (donor.preferred_category or "").casefold() == category]
    recommendations: dict[str, dict[str, Any]] = {}
    for donor in donors[:20]:
        for item in get_donor_recommendations(db, donor.donor_id):
            if category and (item.get("assistance_category") or "").casefold() != category:
                continue
            if any(term in text for term in ("urgent", "immediate")) and (item.get("urgency") or "").casefold() not in {"high", "critical"}:
                continue
            recommendations[item["case_id"]] = item
    items = sorted(
        recommendations.values(),
        key=lambda item: (-LEVELS.get(str(item.get("priority") or "").casefold(), 0), -(_number(item.get("estimated_funding")) - _number(item.get("current_funding"))), item["case_id"]),
    )[:limit]
    cases = [type("LiveCase", (), item)() for item in items]
    return _format_cases(cases, f"Here are {len(cases)} real cases recommended from the live database:")


def answer_live_question(db: Session, question: str) -> str:
    text = question.casefold()
    limit = _limit(question)
    if any(term in text for term in ("recommend", "suitable", "donor-case", "donor interested")):
        return _recommend_cases(db, question, limit)
    cases = _filter_cases(db.scalars(select(Case)).all(), question)
    if "largest number" in text or "most people" in text:
        cases.sort(key=lambda case: (-(_number(case.people_affected)), case.case_id))
    elif "funding gap" in text or "need funding" in text:
        cases.sort(key=lambda case: (-_gap(case), case.case_id))
    else:
        cases.sort(key=lambda case: (-LEVELS.get((case.priority or "").casefold(), 0), -_gap(case), case.case_id))
    return _format_cases(cases[:limit], f"Here are {min(len(cases), limit)} matching live cases:")