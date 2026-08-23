from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.services.source_discovery import discover_sources_for_run, get_sources_for_run

router = APIRouter()


@router.post("/{run_id}/discover-sources")
def discover_sources(run_id: str, db: Session = Depends(get_db)):
    try:
        return discover_sources_for_run(db, run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{run_id}/sources")
def list_sources(run_id: str, db: Session = Depends(get_db)):
    sources = get_sources_for_run(db, run_id)
    return [
        {
            "id": str(s.id),
            "runId": str(s.run_id),
            "taskType": s.task_type,
            "sourceType": s.source_type,
            "title": s.title,
            "url": s.url,
            "publisher": s.publisher,
            "publishedAt": s.published_at.isoformat() if s.published_at else None,
            "authorityScore": float(s.authority_score) if s.authority_score is not None else None,
            "rankScore": float(s.rank_score) if s.rank_score is not None else None,
        }
        for s in sources
    ]