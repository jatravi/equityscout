from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ExtractedEvidence:
    evidence_type: str
    key: str
    value_text: str | None
    value_num: float | None
    value_unit: str | None
    period: str | None
    confidence: float
    locator: dict[str, Any]
    snippet: str | None