from types import SimpleNamespace

from backend.services.assistant_service import answer_live_question, is_live_question, is_mixed_question


def case(case_id, priority="Critical", urgency="High", current=100, estimated=1000):
    return SimpleNamespace(
        case_id=case_id, status="Active", country="Egypt", governorate="Cairo", city="Cairo",
        assistance_category="Food", priority=priority, severity="High", urgency=urgency,
        people_affected=20, current_funding=current, estimated_funding=estimated,
        required_resources="Food parcels",
    )


class FakeScalars:
    def __init__(self, values): self.values = values
    def all(self): return self.values


class FakeDb:
    def __init__(self, cases): self.cases = cases
    def scalars(self, query): return FakeScalars(self.cases)


def test_live_intent_and_real_case_fields():
    assert is_live_question("Show me critical cases")
    answer = answer_live_question(FakeDb([case("CASE-REAL")]), "Show me one critical humanitarian case")
    assert "CASE-REAL" in answer
    assert "Funding gap: 900.00" in answer
    assert answer.count("\n1. ") == 1
    assert is_mixed_question("Why should I prioritize critical cases?")


def test_live_question_with_no_matches_is_explicit():
    answer = answer_live_question(FakeDb([case("CASE-REAL")]), "Show me critical cases in Alexandria")
    assert answer == "No matching cases were found in the live CareHaven database."