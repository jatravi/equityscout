from __future__ import annotations

from collections import defaultdict
from statistics import mean
from sqlalchemy.orm import Session

from apps.api.src.models import ResearchRun, Evidence, Claim


def _score_claim(evidence_rows: list[Evidence], contradiction_tag: str) -> float:
    # simple deterministic v1 score
    base = 0.50
    corroboration = min(0.25, 0.05 * len(evidence_rows))
    avg_ev_conf = mean([float(r.confidence or 0.5) for r in evidence_rows]) if evidence_rows else 0.5
    quality_boost = (avg_ev_conf - 0.5) * 0.30
    contradiction_penalty = 0.0 if contradiction_tag == "NONE" else 0.20
    score = base + corroboration + quality_boost - contradiction_penalty
    return max(0.0, min(1.0, score))


def _detect_metric_conflicts(rows: list[Evidence]) -> set[tuple[str, str | None]]:
    """
    Detect conflicts for FINANCIAL_METRIC on (key, period) where multiple distinct numeric values exist.
    """
    seen: dict[tuple[str, str | None], set[float]] = defaultdict(set)
    for r in rows:
        if r.evidence_type != "FINANCIAL_METRIC" or r.value_num is None:
            continue
        seen[(r.key, r.period)].add(float(r.value_num))
    return {kp for kp, vals in seen.items() if len(vals) > 1}


def build_claims_for_run(db: Session, run_id: str) -> dict:
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise ValueError("Run not found")

    ev_rows = db.query(Evidence).filter(Evidence.run_id == run.id).all()
    if not ev_rows:
        return {
            "runId": str(run.id),
            "totalClaims": 0,
            "countsByType": {"BUSINESS_MODEL": 0, "FINANCIAL_TREND": 0, "PROMOTER_GOVERNANCE": 0},
            "contradictionCounts": {"NONE": 0, "INTRA_DOC": 0, "CROSS_DOC": 0, "METRIC_CONFLICT": 0},
            "avgConfidence": 0.0,
        }

    # clear existing claims for idempotent rebuild
    db.query(Claim).filter(Claim.run_id == run.id).delete(synchronize_session=False)

    by_type: dict[str, list[Evidence]] = defaultdict(list)
    for r in ev_rows:
        by_type[r.evidence_type].append(r)

    metric_conflicts = _detect_metric_conflicts(ev_rows)

    claims_to_create: list[Claim] = []

    # BUSINESS_MODEL claims
    if by_type.get("BUSINESS_SIGNAL"):
        rows = by_type["BUSINESS_SIGNAL"]
        key_counts = defaultdict(int)
        for r in rows:
            key_counts[r.key] += 1

        top = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for key, cnt in top:
            support = [r for r in rows if r.key == key]
            contradiction_tag = "NONE"
            conf = _score_claim(support, contradiction_tag)
            claims_to_create.append(
                Claim(
                    run_id=run.id,
                    company_id=run.company_id,
                    claim_type="BUSINESS_MODEL",
                    claim_text=f"Business signal '{key}' appears {cnt} time(s), indicating directional momentum.",
                    stance="NEUTRAL",
                    confidence=conf,
                    contradiction_tag=contradiction_tag,
                    contradiction_note=None,
                    supporting_evidence_count=len(support),
                    supporting_locators_json=[r.locator_json for r in support[:5]],
                )
            )

    # FINANCIAL_TREND claims
    if by_type.get("FINANCIAL_METRIC"):
        rows = by_type["FINANCIAL_METRIC"]
        by_key_period = defaultdict(list)
        for r in rows:
            by_key_period[(r.key, r.period)].append(r)

        for (key, period), support in by_key_period.items():
            contradiction_tag = "METRIC_CONFLICT" if (key, period) in metric_conflicts else "NONE"
            contradiction_note = "Conflicting numeric values found for same metric/period." if contradiction_tag != "NONE" else None

            nums = [r.value_num for r in support if r.value_num is not None]
            if nums:
                claim_text = f"{key} for {period or 'reported period'} is observed around {nums[0]} (based on extracted evidence)."
            else:
                claim_text = f"{key} is mentioned for {period or 'reported period'}, but numeric normalization is limited in v1."

            conf = _score_claim(support, contradiction_tag)
            claims_to_create.append(
                Claim(
                    run_id=run.id,
                    company_id=run.company_id,
                    claim_type="FINANCIAL_TREND",
                    claim_text=claim_text,
                    stance="NEUTRAL",
                    confidence=conf,
                    contradiction_tag=contradiction_tag,
                    contradiction_note=contradiction_note,
                    supporting_evidence_count=len(support),
                    supporting_locators_json=[r.locator_json for r in support[:5]],
                )
            )

    # PROMOTER_GOVERNANCE claims
    if by_type.get("PROMOTER_HOLDING"):
        rows = by_type["PROMOTER_HOLDING"]
        by_key = defaultdict(list)
        for r in rows:
            by_key[r.key].append(r)

        for key, support in by_key.items():
            contradiction_tag = "NONE"
            text = (
                "Promoter holding signals indicate ownership trend visibility."
                if key == "promoter_holding_pct"
                else "Pledge-related governance signal is present in source evidence."
            )
            conf = _score_claim(support, contradiction_tag)
            claims_to_create.append(
                Claim(
                    run_id=run.id,
                    company_id=run.company_id,
                    claim_type="PROMOTER_GOVERNANCE",
                    claim_text=text,
                    stance="NEUTRAL",
                    confidence=conf,
                    contradiction_tag=contradiction_tag,
                    contradiction_note=None,
                    supporting_evidence_count=len(support),
                    supporting_locators_json=[r.locator_json for r in support[:5]],
                )
            )

    for c in claims_to_create:
        # guard: persist only claims with support
        if c.supporting_evidence_count > 0 and c.supporting_locators_json:
            db.add(c)

    db.commit()

    saved = db.query(Claim).filter(Claim.run_id == run.id).all()
    if not saved:
        return {
            "runId": str(run.id),
            "totalClaims": 0,
            "countsByType": {"BUSINESS_MODEL": 0, "FINANCIAL_TREND": 0, "PROMOTER_GOVERNANCE": 0},
            "contradictionCounts": {"NONE": 0, "INTRA_DOC": 0, "CROSS_DOC": 0, "METRIC_CONFLICT": 0},
            "avgConfidence": 0.0,
        }

    counts_by_type = defaultdict(int)
    contradiction_counts = {"NONE": 0, "INTRA_DOC": 0, "CROSS_DOC": 0, "METRIC_CONFLICT": 0}
    for r in saved:
        counts_by_type[r.claim_type] += 1
        contradiction_counts[r.contradiction_tag] = contradiction_counts.get(r.contradiction_tag, 0) + 1

    return {
        "runId": str(run.id),
        "totalClaims": len(saved),
        "countsByType": {
            "BUSINESS_MODEL": counts_by_type.get("BUSINESS_MODEL", 0),
            "FINANCIAL_TREND": counts_by_type.get("FINANCIAL_TREND", 0),
            "PROMOTER_GOVERNANCE": counts_by_type.get("PROMOTER_GOVERNANCE", 0),
        },
        "contradictionCounts": contradiction_counts,
        "avgConfidence": round(mean([float(x.confidence) for x in saved]), 4),
    }