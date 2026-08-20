from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.schemas import ReportOut
from apps.api.src.services.report_service import get_report_by_run_id

router = APIRouter()

@router.get("/{run_id}", response_model=ReportOut)
def get_report(run_id: str, db: Session = Depends(get_db)):
    report = get_report_by_run_id(db, run_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")

    return ReportOut(
        runId=run_id,
        markdown=report.markdown,
        validationStatus=report.validation_status
    )