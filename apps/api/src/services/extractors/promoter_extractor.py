from __future__ import annotations

import re
from apps.api.src.services.extractors.base import ExtractedEvidence

_HOLDING_PATTERN = r"\b(promoter(?:s)?\s+(?:shareholding|holding))\b[:\-\s]*([0-9]{1,2}(?:\.[0-9]+)?)\s*%"
_PLEDGE_PATTERN = r"\b(pledge|pledged shares?)\b"

def extract_promoter_basics(text: str, locator_base: dict) -> list[ExtractedEvidence]:
    out: list[ExtractedEvidence] = []
    if not text:
        return out

    for m in re.finditer(_HOLDING_PATTERN, text, re.IGNORECASE):
        pct = m.group(2)
        try:
            pct_num = float(pct)
        except Exception:
            pct_num = None

        start = max(0, m.start() - 120)
        end = min(len(text), m.end() + 120)
        snippet = text[start:end].strip()
        loc = {**locator_base, "char_start": m.start(), "char_end": m.end()}

        out.append(
            ExtractedEvidence(
                evidence_type="PROMOTER_HOLDING",
                key="promoter_holding_pct",
                value_text=pct,
                value_num=pct_num,
                value_unit="percent",
                period=None,
                confidence=0.72 if pct_num is not None else 0.58,
                locator=loc,
                snippet=snippet,
            )
        )

    for m in re.finditer(_PLEDGE_PATTERN, text, re.IGNORECASE):
        start = max(0, m.start() - 120)
        end = min(len(text), m.end() + 120)
        snippet = text[start:end].strip()
        loc = {**locator_base, "char_start": m.start(), "char_end": m.end()}

        out.append(
            ExtractedEvidence(
                evidence_type="PROMOTER_HOLDING",
                key="pledge_indicator",
                value_text="mentioned",
                value_num=None,
                value_unit=None,
                period=None,
                confidence=0.60,
                locator=loc,
                snippet=snippet,
            )
        )

    return out