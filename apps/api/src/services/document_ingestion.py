from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.src.models import Document, ParsedDocument
from apps.api.src.services.fetcher import fetch_url
from apps.api.src.services.dedup_utils import canonicalize_url, sha256_bytes
from apps.api.src.services.parsers.dispatcher import parse_document


def ingest_run_documents(db: Session, run_id: str, sources: list) -> dict:
    fetched = deduped = parsed = failed = 0

    for s in sources:
        try:
            original_url = s.url
            canonical_url = canonicalize_url(original_url)

            # Dedup by (company_id, canonical_url)
            existing = (
                db.query(Document)
                .filter(Document.company_id == s.company_id, Document.canonical_url == canonical_url)
                .first()
            )
            if existing:
                deduped += 1
                continue

            fr = fetch_url(original_url)

            if fr.content_bytes is None:
                failed += 1
                doc = Document(
                    company_id=s.company_id,
                    run_id=run_id,
                    source_id=s.id,
                    url=original_url,
                    canonical_url=canonical_url,
                    content_hash="0" * 64,
                    final_url=fr.final_url,
                    http_status=fr.status_code,
                    content_type=fr.headers.get("content-type") if fr.headers else None,
                    content_length=None,
                    fetched_at=fr.fetched_at,
                    raw_bytes=None,
                    parser_status="FAILED",
                    parse_error=fr.error or "fetch_failed",
                )
                db.add(doc)
                db.flush()
                continue

            content_hash = sha256_bytes(fr.content_bytes)

            doc = Document(
                company_id=s.company_id,
                run_id=run_id,
                source_id=s.id,
                url=original_url,
                canonical_url=canonical_url,
                content_hash=content_hash,
                final_url=fr.final_url,
                http_status=fr.status_code,
                content_type=fr.headers.get("content-type") if fr.headers else None,
                content_length=len(fr.content_bytes),
                fetched_at=fr.fetched_at,
                raw_bytes=fr.content_bytes,
                parser_status="PENDING",
                parse_error=None,
            )
            db.add(doc)
            db.flush()
            fetched += 1

            pr = parse_document(fr.content_bytes, content_type=doc.content_type)

            parsed_row = ParsedDocument(
                document_id=doc.id,
                title=pr.title,
                plain_text=pr.plain_text,
                text_length=len(pr.plain_text or ""),
                metadata_json=pr.metadata or {},
            )
            db.add(parsed_row)

            doc.parser_status = "PARSED"
            parsed += 1

        except Exception as ex:
            failed += 1
            # best effort continue
            continue

    db.commit()

    return {
        "runId": run_id,
        "totalSources": len(sources),
        "fetched": fetched,
        "deduped": deduped,
        "parsed": parsed,
        "failed": failed,
    }