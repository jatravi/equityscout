# integrate with your existing router/module names
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.services.diagnostics_service import build_diagnostics_payload, StageMetrics
from apps.api.src.db.session import get_db
from apps.api.src.db import models

router = APIRouter()

@router.get("/research-runs/{run_id}/diagnostics")
def get_run_diagnostics(run_id: str, db: Session = Depends(get_db)):
    run = db.query(models.ResearchRun).filter(models.ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Source counts (adjust fields to your schema)
    source_total = db.query(models.Source).filter(models.Source.run_id == run_id).count()
    source_success = db.query(models.Source).filter(
        models.Source.run_id == run_id,
        models.Source.status.in_(["OK", "FETCHED", "SUCCESS"])
    ).count()

    # Document/parser counts
    docs_total = db.query(models.Document).filter(models.Document.run_id == run_id).count()
    docs_parsed = db.query(models.Document).filter(
        models.Document.run_id == run_id,
        models.Document.parser_status == "PARSED"
    ).count()

    evidence_count = db.query(models.Evidence).filter(models.Evidence.run_id == run_id).count()
    claims_count = db.query(models.Claim).filter(models.Claim.run_id == run_id).count()

    latest_report = (
        db.query(models.Report)
        .filter(models.Report.run_id == run_id)
        .order_by(models.Report.created_at.desc())
        .first()
    )

    citation_count = int(getattr(latest_report, "citation_count", 0) or 0)
    report_validation_status = getattr(latest_report, "validation_status", "PENDING") or "PENDING"
    validation_error_count = int(getattr(latest_report, "validation_error_count", 0) or 0)

    # Optional run telemetry table (if exists in your schema)
    telemetry = (
        db.query(models.RunTelemetry)
        .filter(models.RunTelemetry.run_id == run_id)
        .order_by(models.RunTelemetry.created_at.desc())
        .first()
        if hasattr(models, "RunTelemetry")
        else None
    )

    token_input = int(getattr(telemetry, "token_input", 0) or 0)
    token_output = int(getattr(telemetry, "token_output", 0) or 0)
    estimated_cost = float(getattr(telemetry, "estimated_cost", 0.0) or 0.0)

    stage = StageMetrics(
        discover_ms=int(getattr(run, "discover_ms", 0) or 0),
        ingest_ms=int(getattr(run, "ingest_ms", 0) or 0),
        extract_ms=int(getattr(run, "extract_ms", 0) or 0),
        claims_ms=int(getattr(run, "claims_ms", 0) or 0),
        report_ms=int(getattr(run, "report_ms", 0) or 0),
    )

    return build_diagnostics_payload(
        run_id=run_id,
        source_total=source_total,
        source_success=source_success,
        docs_total=docs_total,
        docs_parsed=docs_parsed,
        evidence_count=evidence_count,
        claims_count=claims_count,
        citation_count=citation_count,
        report_validation_status=report_validation_status,
        validation_error_count=validation_error_count,
        token_input=token_input,
        token_output=token_output,
        estimated_cost=estimated_cost,
        stage_metrics=stage,
    )