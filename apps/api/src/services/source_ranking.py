from datetime import datetime, timezone
from typing import Dict


BASE_AUTHORITY: Dict[str, float] = {
    "NSE_ANNOUNCEMENT": 1.00,
    "NSE_RESULTS": 1.00,
    "BSE_FILING": 1.00,
    "COMPANY_IR": 0.80,
    "NEWS": 0.40,
}


def freshness_score(published_at) -> float:
    if not published_at:
        return 0.3
    days_old = max((datetime.now(timezone.utc) - published_at).days, 0)
    if days_old <= 7:
        return 1.0
    if days_old <= 30:
        return 0.8
    if days_old <= 90:
        return 0.6
    return 0.3


def relevance_score(task_type: str, source_type: str) -> float:
    task_type = task_type.upper()
    if task_type == "FINANCIAL" and source_type in {"NSE_RESULTS", "BSE_FILING"}:
        return 1.0
    if task_type == "PROMOTER" and source_type in {"BSE_FILING", "NSE_ANNOUNCEMENT"}:
        return 0.9
    if task_type == "BUSINESS" and source_type in {"NSE_ANNOUNCEMENT", "COMPANY_IR"}:
        return 0.9
    return 0.6


def score_source(task_type: str, source_type: str, published_at) -> float:
    authority = BASE_AUTHORITY.get(source_type, 0.5)
    relevance = relevance_score(task_type, source_type)
    fresh = freshness_score(published_at)
    return round((0.6 * authority) + (0.25 * relevance) + (0.15 * fresh), 4)