from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.models import ResearchRun, Source, Document, ParsedDocument
from apps.api.src.schemas import IngestDocsResponse, DocumentsListResponse, DocumentItem
from apps.api.src.services.document_ingestion import ingest_run_documents

router = APIRouter()


@router.post("/research-runs/{run_id}/ingest-docs", response_model=IngestDocsResponse)
def ingest_docs(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    sources = db.query(Source).filter(Source.run_id == run_id).all()
    summary = ingest_run_documents(db, run_id, sources)
    return summary


@router.get("/research-runs/{run_id}/documents", response_model=DocumentsListResponse)
def list_documents(run_id: str, db: Session = Depends(get_db)):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rows = (
        db.query(Document, ParsedDocument)
        .outerjoin(ParsedDocument, ParsedDocument.document_id == Document.id)
        .filter(Document.run_id == run_id)
        .order_by(Document.fetched_at.desc())
        .all()
    )

    items = []
    for d, p in rows:
        items.append(
            DocumentItem(
                documentId=str(d.id),
                sourceId=str(d.source_id) if d.source_id else None,
                url=d.url,
                canonicalUrl=d.canonical_url,
                contentHash=d.content_hash,
                httpStatus=d.http_status,
                contentType=d.content_type,
                fetchedAt=d.fetched_at,
                parserStatus=d.parser_status,
                parseTitle=p.title if p else None,
                parseLength=p.text_length if p else None,
                parseMetadata=p.metadata_json if p else None,
            )
        )

    return DocumentsListResponse(runId=run_id, items=items)