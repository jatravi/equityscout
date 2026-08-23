import uuid
from uuid import UUID
from collections import defaultdict
from typing import List, Dict
from sqlalchemy.orm import Session

from apps.api.src import db
from apps.api.src.models import ResearchRun, ResearchTask, Company, Source
from apps.api.src.services.company_resolver import CompanyResolver
from apps.api.src.services.providers.nse_provider import NSEProvider
from apps.api.src.services.providers.bse_provider import BSEProvider
from apps.api.src.services.providers.ir_provider import IRProvider
from apps.api.src.services.source_ranking import score_source
from sqlalchemy.dialects.postgresql import insert as pg_insert

def discover_sources_for_run(db: Session, run_id: str) -> Dict:
    try:
        run_uuid = UUID(run_id)
    except ValueError:
        raise ValueError("Invalid run id format")

    run = db.query(ResearchRun).filter(ResearchRun.id == run_uuid).first()
    if not run:
        raise ValueError("Research run not found")

    company = db.query(Company).filter(Company.id == run.company_id).first()
    if not company:
        raise ValueError("Company not found for run")

    resolver = CompanyResolver(db)
    resolved = resolver.resolve(company.legal_name)

    tasks = db.query(ResearchTask).filter(ResearchTask.run_id == run.id).all()

    nse = NSEProvider()
    bse = BSEProvider()
    ir = IRProvider()

    inserted = 0
    updated = 0
    by_type = defaultdict(int)

    for task in tasks:
        task_type = task.task_type

        discovered = []
        discovered.extend(nse.discover(resolved.legal_name, resolved.nse_symbol, task_type))
        discovered.extend(bse.discover(resolved.legal_name, resolved.bse_code, task_type))
        discovered.extend(ir.discover(resolved.legal_name, task_type))

        for d in discovered:
            rank = score_source(
                task_type=task_type,
                source_type=d.source_type,
                published_at=d.published_at,
            )
            authority = 1.0 if d.source_type.startswith(("NSE", "BSE")) else 0.8
            meta = d.metadata if isinstance(d.metadata, dict) else {}

            # DEDUPE by (company_id, url) to satisfy unique index
            existing = (
                db.query(Source)
                .filter(Source.company_id == company.id, Source.url == d.url)
                .first()
            )

            if existing:
                # keep best score / enrich record
                if existing.rank_score is None or rank > float(existing.rank_score):
                    existing.rank_score = rank
                if existing.authority_score is None or authority > float(existing.authority_score):
                    existing.authority_score = authority

                # optional metadata refresh
                existing.task_type = task_type
                existing.source_type = d.source_type
                existing.title = d.title
                existing.publisher = d.publisher
                existing.published_at = d.published_at
                existing.metadata_json = meta

                updated += 1
                by_type[d.source_type] += 1
                continue
            stmt = pg_insert(Source.__table__).values(
                id=uuid.uuid4(),
                run_id=run.id,
                company_id=company.id,
                task_type=task_type,
                source_type=d.source_type,
                title=d.title,
                url=d.url,
                publisher=d.publisher,
                published_at=d.published_at,
                authority_score=authority,
                rank_score=rank,
                metadata_json=meta,
            )

            # unique index is on (url, company_id)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["url", "company_id"],
                set_={
                    "run_id": run.id,
                    "task_type": task_type,
                    "source_type": d.source_type,
                    "title": d.title,
                    "publisher": d.publisher,
                    "published_at": d.published_at,
                    "authority_score": authority,
                    "rank_score": rank,
                    "metadata_json": meta,
                },
            )

            db.execute(upsert_stmt)
            source = Source(
                id=uuid.uuid4(),
                run_id=run.id,
                company_id=company.id,
                task_type=task_type,
                source_type=d.source_type,
                title=d.title,
                url=d.url,
                publisher=d.publisher,
                published_at=d.published_at,
                authority_score=authority,
                rank_score=rank,
                metadata_json=meta,
            )
            # db.add(source)
            inserted += 1
            by_type[d.source_type] += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "runId": str(run.id),
        "company": company.legal_name,
        "resolvedMatchType": resolved.match_type,
        "totalDiscovered": inserted,
        "totalUpdated": updated,
        "countsBySourceType": dict(by_type),
    }


def get_sources_for_run(db: Session, run_id: str) -> List[Source]:
    run_uuid = UUID(run_id)
    return (
        db.query(Source)
        .filter(Source.run_id == run_uuid)
        .order_by(Source.rank_score.desc(), Source.published_at.desc())
        .all()
    )