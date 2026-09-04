from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.models import ResearchRun, Claim
from apps.api.src.schemas import BuildClaimsResponse, ClaimsListResponse, ClaimItem
from apps.api.src.services.claims_builder import build_claims_for_run

router = APIRouter()

@router.post("/research-runs/{run_id}/build-claims", response_model=BuildClaimsResponse)
def build_claims(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return build_claims_for_run(db, run_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")

@router.get("/research-runs/{run_id}/claims", response_model=ClaimsListResponse)
def list_claims(
    run_id: str,
    claim_type: str | None = Query(default=None),
    min_confidence: float | None = Query(default=None),
    contradiction_tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    q = db.query(Claim).filter(Claim.run_id == run.id)

    if claim_type:
        q = q.filter(Claim.claim_type == claim_type)
    if min_confidence is not None:
        q = q.filter(Claim.confidence >= min_confidence)
    if contradiction_tag:
        q = q.filter(Claim.contradiction_tag == contradiction_tag)

    rows = q.order_by(Claim.confidence.desc(), Claim.created_at.desc()).all()

    items = [
        ClaimItem(
            claimId=str(r.id),
            runId=str(r.run_id),
            companyId=str(r.company_id),
            claimType=r.claim_type,  # type: ignore[arg-type]
            claimText=r.claim_text,
            stance=r.stance,
            confidence=float(r.confidence),
            contradictionTag=r.contradiction_tag,  # type: ignore[arg-type]
            contradictionNote=r.contradiction_note,
            supportingEvidenceCount=r.supporting_evidence_count,
            supportingLocators=r.supporting_locators_json or [],
            createdAt=r.created_at,
        )
        for r in rows
    ]
    return ClaimsListResponse(runId=str(run.id), items=items)