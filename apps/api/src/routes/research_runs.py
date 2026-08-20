from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from schemas import CreateResearchRunRequest, CreateResearchRunResponse, ResearchRunOut, ResearchTaskOut
from services.research_run_service import create_research_run, get_research_run

router = APIRouter()

@router.post("", response_model=CreateResearchRunResponse)
def create_run(payload: CreateResearchRunRequest, db: Session = Depends(get_db)):
    run, company = create_research_run(db, payload.company)
    return CreateResearchRunResponse(
        runId=str(run.id),
        status=run.status,
        company=company.legal_name
    )

@router.get("/{run_id}", response_model=ResearchRunOut)
def get_run(run_id: str, db: Session = Depends(get_db)):
    result = get_research_run(db, run_id)
    if not result:
        raise HTTPException(status_code=404, detail="Research run not found")

    run, company, tasks = result
    return ResearchRunOut(
        runId=str(run.id),
        company=company.legal_name,
        status=run.status,
        startedAt=run.started_at.isoformat() if run.started_at else None,
        finishedAt=run.finished_at.isoformat() if run.finished_at else None,
        errorMessage=run.error_message,
        tasks=[ResearchTaskOut(id=str(t.id), taskType=t.task_type, status=t.status) for t in tasks]
    )