from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CaseLevel = Literal["Low", "Medium", "High", "Critical"]


class CaseAnalysisResult(BaseModel):
    """Validated information extracted from a humanitarian case description."""

    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1, max_length=200)
    assistance: list[str] = Field(min_length=1)
    people_affected: int = Field(ge=1)
    severity: CaseLevel
    summary: str = Field(min_length=1, max_length=4000)

    def model_post_init(self, __context: object) -> None:
        if any(not item.strip() for item in self.assistance):
            raise ValueError("assistance entries must not be empty")
