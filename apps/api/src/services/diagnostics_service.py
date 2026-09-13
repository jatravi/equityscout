from __future__ import annotations

from decimal import Decimal
from alembic.environment import Any
from pydantic.dataclasses import dataclass
from pydantic.dataclasses import dataclass
from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.api.src.models import (
    ResearchRun,
    Source,
    Document,
    ParsedDocument,
    Evidence,
    Claim,
    Report,
    RunDiagnostics,
)

@dataclass
class StageMetrics:
    discover_ms: int = 0
    ingest_ms: int = 0
    extract_ms: int = 0
    claims_ms: int = 0
    report_ms: int = 0

def safe_rate(num: int | float, den: int | float) -> float:
    if den is None or den == 0:
        return 0.0
    v = float(num) / float(den)
    if v < 0:
        return 0.0
    if v > 1:
        return 1.0
    return round(v, 4)

def to_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default

def to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default

def build_diagnostics_payload(
    *,
    run_id: str,
    source_total: int,
    source_success: int,
    docs_total: int,
    docs_parsed: int,
    evidence_count: int,
    claims_count: int,
    citation_count: int,
    report_validation_status: str,
    validation_error_count: int,
    token_input: int = 0,
    token_output: int = 0,
    estimated_cost: float = 0.0,
    stage_metrics: StageMetrics | None = None,
) -> dict[str, Any]:
    sm = stage_metrics or StageMetrics()

    payload = {
        "runId": run_id,
        "tokenInput": to_int(token_input),
        "tokenOutput": to_int(token_output),
        "estimatedCost": round(to_float(estimated_cost), 6),
        "sourcesTotal": to_int(source_total),
        "sourcesSuccess": to_int(source_success),
        "sourceSuccessRate": safe_rate(source_success, source_total),
        "docsTotal": to_int(docs_total),
        "docsParsed": to_int(docs_parsed),
        "parserFailureRate": safe_rate(max(docs_total - docs_parsed, 0), docs_total),
        "evidenceCount": to_int(evidence_count),
        "claimsCount": to_int(claims_count),
        "citationCount": to_int(citation_count),
        "reportValidationStatus": report_validation_status or "PENDING",
        "validationErrorCount": to_int(validation_error_count),
        "discoverMs": to_int(sm.discover_ms),
        "ingestMs": to_int(sm.ingest_ms),
        "extractMs": to_int(sm.extract_ms),
        "claimsMs": to_int(sm.claims_ms),
        "reportMs": to_int(sm.report_ms),
    }
    return payload

def upsert_run_diagnostics(
    db: Session,
    run_id: str,
    token_input: int = 0,
    token_output: int = 0,
    estimated_cost: float = 0.0,
    discover_ms: int = 0,
    ingest_ms: int = 0,
    extract_ms: int = 0,
    claims_ms: int = 0,
    report_ms: int = 0,
) -> RunDiagnostics:
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise ValueError("Run not found")

    sources_total = db.query(Source).filter(Source.run_id == run.id).count()
    docs_total = db.query(Document).filter(Document.run_id == run.id).count()
    docs_parsed = db.query(Document).filter(Document.run_id == run.id, Document.parser_status == "PARSED").count()
    evidence_count = db.query(Evidence).filter(Evidence.run_id == run.id).count()
    claims_count = db.query(Claim).filter(Claim.run_id == run.id).count()

    rep = db.query(Report).filter(Report.run_id == run.id, Report.version == "v1").first()
    citation_count = int(rep.citation_count) if rep else 0
    report_validation_status = getattr(rep, "validation_status", "PENDING") if rep else "PENDING"
    validation_error_count = len(getattr(rep, "validation_errors_json", []) or []) if rep else 0

    sources_success = docs_total  # proxy: successful fetch persisted as document row
    source_success_rate = safe_rate(sources_success, sources_total)
    parser_failure_rate = safe_rate(max(docs_total - docs_parsed, 0), docs_total)

    row = db.query(RunDiagnostics).filter(RunDiagnostics.run_id == run.id).first()
    if not row:
        row = RunDiagnostics(
            run_id=run.id,
            company_id=run.company_id,
        )

    row.token_input = int(token_input)
    row.token_output = int(token_output)
    row.estimated_cost = Decimal(str(estimated_cost))

    row.sources_total = int(sources_total)
    row.sources_success = int(sources_success)
    row.source_success_rate = Decimal(str(source_success_rate))

    row.docs_total = int(docs_total)
    row.docs_parsed = int(docs_parsed)
    row.parser_failure_rate = Decimal(str(parser_failure_rate))

    row.evidence_count = int(evidence_count)
    row.claims_count = int(claims_count)
    row.citation_count = int(citation_count)

    row.report_validation_status = report_validation_status
    row.validation_error_count = int(validation_error_count)

    row.discover_ms = int(discover_ms)
    row.ingest_ms = int(ingest_ms)
    row.extract_ms = int(extract_ms)
    row.claims_ms = int(claims_ms)
    row.report_ms = int(report_ms)

    db.add(row)
    db.commit()
    db.refresh(row)
    return row