from __future__ import annotations

from collections import Counter
from apps.api.src.models import Claim


def build_verdict_v1(claims: list[Claim]) -> dict:
    """
    Narrative-first verdict strategy.
    Uses confidence + contradiction as guidance, not rigid numeric gating.
    """
    if not claims:
        return {
            "verdict_label": "CAUTIOUS",
            "verdict_summary": "Insufficient claim coverage is available for a directional view at this stage.",
            "key_supporting_points": [],
            "key_risks": ["Limited supported claims available."],
        }

    contradiction_counts = Counter([c.contradiction_tag for c in claims])
    avg_conf = sum(float(c.confidence) for c in claims) / len(claims)

    high_conf = [c for c in claims if float(c.confidence) >= 0.65]
    risk_claims = [c for c in claims if c.contradiction_tag != "NONE"]

    if contradiction_counts.get("METRIC_CONFLICT", 0) >= 2 or len(risk_claims) >= max(2, len(claims) // 3):
        verdict_label = "CAUTIOUS"
    elif avg_conf >= 0.68 and len(high_conf) >= max(2, len(claims) // 2):
        verdict_label = "POSITIVE"
    else:
        verdict_label = "MIXED"

    top_support = sorted(claims, key=lambda x: float(x.confidence), reverse=True)[:5]
    key_supporting_points = [c.claim_text for c in top_support]

    key_risks = []
    if contradiction_counts.get("METRIC_CONFLICT", 0) > 0:
        key_risks.append("Some financial metrics show conflicting values across sources.")
    if contradiction_counts.get("CROSS_DOC", 0) > 0:
        key_risks.append("Cross-document narrative inconsistencies are present.")
    if contradiction_counts.get("INTRA_DOC", 0) > 0:
        key_risks.append("Intra-document inconsistencies were detected.")
    if not key_risks:
        key_risks.append("No major contradiction flags detected in current claim set.")

    verdict_summary = (
        f"Overall view is {verdict_label.lower()} based on {len(claims)} supported claims "
        f"(avg confidence {avg_conf:.2f}). "
        f"Interpretation remains sensitive to evidence coverage and contradiction signals."
    )

    return {
        "verdict_label": verdict_label,
        "verdict_summary": verdict_summary,
        "key_supporting_points": key_supporting_points,
        "key_risks": key_risks,
    }