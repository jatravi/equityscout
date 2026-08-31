from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.models import Evidence, ResearchRun
from apps.api.src.schemas import ExtractEvidenceResponse, EvidenceListResponse, EvidenceItem
from apps.api.src.services.evidence_extraction import extract_evidence_for_run

router = APIRouter()

@router.post("/research-runs/{run_id}/extract-evidence", response_model=ExtractEvidenceResponse)
def extract_evidence(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        return extract_evidence_for_run(db, run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")

@router.get("/research-runs/{run_id}/evidence", response_model=EvidenceListResponse)
def list_evidence(
    run_id: str,
    evidence_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    q = db.query(Evidence).filter(Evidence.run_id == run.id)
    if evidence_type:
        q = q.filter(Evidence.evidence_type == evidence_type)

    rows = q.order_by(Evidence.created_at.desc()).all()

    items = [
        EvidenceItem(
            evidenceId=str(r.id),
            runId=str(r.run_id),
            companyId=str(r.company_id),
            documentId=str(r.document_id),
            evidenceType=r.evidence_type,  # type: ignore[arg-type]
            key=r.key,
            valueText=r.value_text,
            valueNum=r.value_num,
            valueUnit=r.value_unit,
            period=r.period,
            confidence=r.confidence,
            locator=r.locator_json,
            snippet=r.snippet,
            createdAt=r.created_at,
        )
        for r in rows
    ]
    return EvidenceListResponse(runId=run_id, items=items)