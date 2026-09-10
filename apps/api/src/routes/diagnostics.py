from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.models import ResearchRun, RunDiagnostics
from apps.api.src.schemas import RunDiagnosticsResponse
from apps.api.src.services.diagnostics_service import upsert_run_diagnostics

router = APIRouter()

@router.get("/research-runs/{run_id}/diagnostics", response_model=RunDiagnosticsResponse)
def get_run_diagnostics(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    row = db.query(RunDiagnostics).filter(RunDiagnostics.run_id == run.id).first()
    if not row:
        row = upsert_run_diagnostics(db=db, run_id=run_id)

    return RunDiagnosticsResponse(
        runId=str(row.run_id),
        companyId=str(row.company_id),
        tokenInput=int(row.token_input),
        tokenOutput=int(row.token_output),
        estimatedCost=float(row.estimated_cost),
        sourcesTotal=int(row.sources_total),
        sourcesSuccess=int(row.sources_success),
        sourceSuccessRate=float(row.source_success_rate),
        docsTotal=int(row.docs_total),
        docsParsed=int(row.docs_parsed),
        parserFailureRate=float(row.parser_failure_rate),
        evidenceCount=int(row.evidence_count),
        claimsCount=int(row.claims_count),
        citationCount=int(row.citation_count),
        reportValidationStatus=row.report_validation_status,
        validationErrorCount=int(row.validation_error_count),
        discoverMs=int(row.discover_ms),
        ingestMs=int(row.ingest_ms),
        extractMs=int(row.extract_ms),
        claimsMs=int(row.claims_ms),
        reportMs=int(row.report_ms),
        createdAt=row.created_at,
        updatedAt=row.updated_at,
    )