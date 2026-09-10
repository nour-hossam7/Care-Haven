from typing import Any
from .client import ApiClient
def analyze_case(client: ApiClient, case_id: str) -> dict[str, Any]: return client.post(f"/ai/cases/{case_id}/analyze")
def calculate_priority(client: ApiClient, case_id: str) -> dict[str, Any]: return client.post(f"/ai/cases/{case_id}/calculate-priority")
def hybrid_analysis(client: ApiClient, case_id: str) -> dict[str, Any]: return client.post(f"/ai/cases/{case_id}/hybrid-analysis")
