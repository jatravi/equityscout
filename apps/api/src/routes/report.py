from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.models import ResearchRun, Report
from apps.api.src.schemas import GenerateReportResponse, ReportResponse
from apps.api.src.services.report_builder import generate_report_for_run

router = APIRouter()

@router.post("/research-runs/{run_id}/generate-report", response_model=GenerateReportResponse)
def generate_report(
    run_id: str,
    include_appendix: bool = Query(default=True),
    min_confidence: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return generate_report_for_run(
            db=db,
            run_id=run_id,
            version="v1",
            include_appendix=include_appendix,
            min_confidence=min_confidence,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")

@router.get("/research-runs/{run_id}/report", response_model=ReportResponse)
def get_report(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    row = (
        db.query(Report)
        .filter(Report.run_id == run.id, Report.version == "v1")
        .order_by(Report.created_at.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Report not found. Generate first via /generate-report")

    return ReportResponse(
        runId=str(run.id),
        version=row.version,
        verdictLabel=row.verdict_label,
        verdictSummary=row.verdict_summary,
        citationCount=int(row.citation_count),
        reportMarkdown=row.report_markdown,
        createdAt=row.created_at,
    )