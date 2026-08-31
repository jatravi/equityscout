from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.src.models import ResearchRun, Document, ParsedDocument, Evidence
from apps.api.src.services.extractors.business_extractor import extract_business_signals
from apps.api.src.services.extractors.financial_extractor import extract_financial_metrics
from apps.api.src.services.extractors.promoter_extractor import extract_promoter_basics


def extract_evidence_for_run(db: Session, run_id: str) -> dict:
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise ValueError("Run not found")

    rows = (
        db.query(Document, ParsedDocument)
        .join(ParsedDocument, ParsedDocument.document_id == Document.id)
        .filter(Document.run_id == run_id, Document.parser_status == "PARSED")
        .all()
    )

    extracted = 0
    deduped = 0
    failed_documents = 0
    counts = {"BUSINESS_SIGNAL": 0, "FINANCIAL_METRIC": 0, "PROMOTER_HOLDING": 0}

    for d, p in rows:
        try:
            text = p.plain_text or ""
            locator_base = {
                "url": d.url,
                "canonical_url": d.canonical_url,
                "title": p.title,
            }

            candidates = []
            candidates.extend(extract_business_signals(text, locator_base))
            candidates.extend(extract_financial_metrics(text, locator_base))
            candidates.extend(extract_promoter_basics(text, locator_base))

            for ev in candidates:
                exists = (
                    db.query(Evidence)
                    .filter(
                        Evidence.run_id == run.id,
                        Evidence.document_id == d.id,
                        Evidence.evidence_type == ev.evidence_type,
                        Evidence.key == ev.key,
                        Evidence.value_text.is_(ev.value_text) if ev.value_text is None else Evidence.value_text == ev.value_text,
                        Evidence.value_num.is_(ev.value_num) if ev.value_num is None else Evidence.value_num == ev.value_num,
                        Evidence.value_unit.is_(ev.value_unit) if ev.value_unit is None else Evidence.value_unit == ev.value_unit,
                        Evidence.period.is_(ev.period) if ev.period is None else Evidence.period == ev.period,
                    )
                    .first()
                )

                if exists:
                    deduped += 1
                    continue

                row = Evidence(
                    run_id=run.id,
                    company_id=d.company_id,
                    document_id=d.id,
                    evidence_type=ev.evidence_type,
                    key=ev.key,
                    value_text=ev.value_text,
                    value_num=ev.value_num,
                    value_unit=ev.value_unit,
                    period=ev.period,
                    confidence=ev.confidence,
                    locator_json=ev.locator or {},
                    snippet=ev.snippet,
                )
                db.add(row)
                extracted += 1
                counts[ev.evidence_type] = counts.get(ev.evidence_type, 0) + 1

        except Exception:
            failed_documents += 1
            continue

    db.commit()

    return {
        "runId": run_id,
        "processedDocuments": len(rows),
        "extracted": extracted,
        "deduped": deduped,
        "failedDocuments": failed_documents,
        "countsByType": counts,
    }