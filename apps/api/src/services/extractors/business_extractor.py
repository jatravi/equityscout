from __future__ import annotations

import re
from apps.api.src.services.extractors.base import ExtractedEvidence

_PATTERNS = {
    "capacity_expansion": r"\b(capacity expansion|expand(?:ing)? capacity|new plant)\b",
    "order_win": r"\b(order win|won order|new contract)\b",
    "capex": r"\b(capex|capital expenditure)\b",
    "guidance": r"\b(guidance|outlook|forecast)\b",
    "regulatory_event": r"\b(regulatory|litigation|penalty|notice)\b",
}

def extract_business_signals(text: str, locator_base: dict) -> list[ExtractedEvidence]:
    out: list[ExtractedEvidence] = []
    if not text:
        return out

    lower = text.lower()
    for key, pattern in _PATTERNS.items():
        for m in re.finditer(pattern, lower):
            start = max(0, m.start() - 120)
            end = min(len(text), m.end() + 120)
            snippet = text[start:end].strip()
            loc = {**locator_base, "char_start": m.start(), "char_end": m.end()}
            out.append(
                ExtractedEvidence(
                    evidence_type="BUSINESS_SIGNAL",
                    key=key,
                    value_text=m.group(0),
                    value_num=None,
                    value_unit=None,
                    period=None,
                    confidence=0.65,
                    locator=loc,
                    snippet=snippet,
                )
            )
    return out