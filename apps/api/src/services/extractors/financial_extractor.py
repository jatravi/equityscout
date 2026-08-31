from __future__ import annotations

import re
from apps.api.src.services.extractors.base import ExtractedEvidence

# very simple v1 patterns; improve later for tables/locale formats
_PATTERNS = {
    "revenue": r"\b(revenue|total income)\b[:\-\s]*([0-9][0-9,\.]*)\s*(cr|crore|mn|million|bn|billion)?",
    "net_profit": r"\b(net profit|profit after tax|pat)\b[:\-\s]*([0-9][0-9,\.]*)\s*(cr|crore|mn|million|bn|billion)?",
    "ebitda_margin": r"\b(ebitda margin|operating margin)\b[:\-\s]*([0-9][0-9,\.]*)\s*%",
    "debt": r"\b(total debt|net debt|debt)\b[:\-\s]*([0-9][0-9,\.]*)\s*(cr|crore|mn|million|bn|billion)?",
    "cashflow_ops": r"\b(operating cash flow|cash flow from operations|cfo)\b[:\-\s]*([0-9][0-9,\.]*)\s*(cr|crore|mn|million|bn|billion)?",
}
_PERIOD_PATTERN = r"\b(Q[1-4]\s*FY\s*\d{2,4}|FY\s*\d{2,4}|H[1-2]\s*FY\s*\d{2,4})\b"

def _to_float(num_str: str) -> float | None:
    try:
        return float(num_str.replace(",", ""))
    except Exception:
        return None

def extract_financial_metrics(text: str, locator_base: dict) -> list[ExtractedEvidence]:
    out: list[ExtractedEvidence] = []
    if not text:
        return out

    period_match = re.search(_PERIOD_PATTERN, text, re.IGNORECASE)
    period = period_match.group(0).strip() if period_match else None

    for key, pattern in _PATTERNS.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            raw_val = m.group(2) if m.lastindex and m.lastindex >= 2 else None
            unit = m.group(3) if m.lastindex and m.lastindex >= 3 else None
            value_num = _to_float(raw_val) if raw_val else None

            start = max(0, m.start() - 120)
            end = min(len(text), m.end() + 120)
            snippet = text[start:end].strip()
            loc = {**locator_base, "char_start": m.start(), "char_end": m.end()}

            out.append(
                ExtractedEvidence(
                    evidence_type="FINANCIAL_METRIC",
                    key=key,
                    value_text=raw_val,
                    value_num=value_num,
                    value_unit=unit.lower() if unit else None,
                    period=period,
                    confidence=0.70 if value_num is not None else 0.55,
                    locator=loc,
                    snippet=snippet,
                )
            )
    return out