from __future__ import annotations

from collections import defaultdict
from sqlalchemy.orm import Session
from apps.api.src.models import ResearchRun, Claim, Evidence, Report
from apps.api.src.services.verdict_strategy import build_verdict_v1


def _build_citation_index(evidence_rows: list[Evidence]) -> tuple[dict[str, str], list[str]]:
    """
    Returns:
      evidence_id -> citation_label (E1, E2...)
      appendix_lines
    """
    citation_map: dict[str, str] = {}
    appendix_lines: list[str] = []
    idx = 1
    for ev in evidence_rows:
        ev_id = str(ev.id)
        if ev_id in citation_map:
            continue
        tag = f"E{idx}"
        citation_map[ev_id] = tag
        loc = ev.locator_json or {}
        title = loc.get("title") or ev.key
        url = loc.get("canonical_url") or loc.get("url") or "n/a"
        snippet = (ev.snippet or "").strip().replace("\n", " ")
        if len(snippet) > 180:
            snippet = snippet[:180] + "..."
        appendix_lines.append(f"- [{tag}] {title} — {url} (snippet: \"{snippet}\")")
        idx += 1
    return citation_map, appendix_lines


def _citations_for_claim(claim: Claim, ev_by_locator_key: dict[str, str]) -> str:
    tags = []
    for loc in (claim.supporting_locators_json or []):
        key = f"{loc.get('canonical_url') or loc.get('url') or ''}|{loc.get('char_start') or ''}|{loc.get('char_end') or ''}"
        tag = ev_by_locator_key.get(key)
        if tag and tag not in tags:
            tags.append(tag)
    return "".join([f"[{t}]" for t in tags[:3]])


def generate_report_for_run(db: Session, run_id: str, version: str = "v1", include_appendix: bool = True, min_confidence: float | None = None) -> dict:
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise ValueError("Run not found")

    cq = db.query(Claim).filter(Claim.run_id == run.id)
    if min_confidence is not None:
        cq = cq.filter(Claim.confidence >= min_confidence)
    claims = cq.order_by(Claim.confidence.desc(), Claim.created_at.desc()).all()

    eq = db.query(Evidence).filter(Evidence.run_id == run.id).order_by(Evidence.created_at.desc())
    evidence_rows = eq.all()

    verdict = build_verdict_v1(claims)

    citation_map, appendix_lines = _build_citation_index(evidence_rows)

    # map locator fingerprint -> citation tag
    ev_by_locator_key: dict[str, str] = {}
    for ev in evidence_rows:
        ev_id = str(ev.id)
        tag = citation_map.get(ev_id)
        if not tag:
            continue
        loc = ev.locator_json or {}
        fp = f"{loc.get('canonical_url') or loc.get('url') or ''}|{loc.get('char_start') or ''}|{loc.get('char_end') or ''}"
        ev_by_locator_key[fp] = tag

    by_type = defaultdict(list)
    for c in claims:
        by_type[c.claim_type].append(c)

    def claim_lines(claim_type: str) -> list[str]:
        lines = []
        for c in by_type.get(claim_type, [])[:8]:
            cites = _citations_for_claim(c, ev_by_locator_key)
            lines.append(f"- {c.claim_text} {cites}".rstrip())
        if not lines:
            lines.append("- Limited claim coverage available in this section.")
        return lines

    contradiction_lines = []
    contradicted = [c for c in claims if c.contradiction_tag != "NONE"]
    if contradicted:
        for c in contradicted[:8]:
            contradiction_lines.append(
                f"- ({c.contradiction_tag}) {c.claim_text}"
                + (f" — {c.contradiction_note}" if c.contradiction_note else "")
            )
    else:
        contradiction_lines.append("- No major contradiction tags detected in current claim set.")

    supporting_points = [f"- {x}" for x in verdict["key_supporting_points"][:5]]
    if not supporting_points:
        supporting_points = ["- No supporting points available."]

    risk_points = [f"- {x}" for x in verdict["key_risks"][:5]]
    if not risk_points:
        risk_points = ["- No major risks captured."]

    report_lines = [
        "# EquityScout Research Report",
        "",
        f"Run ID: `{run_id}`",
        f"Version: `{version}`",
        "",
        "## Company Snapshot",
        "- Snapshot generated from discovered sources and extracted evidence.",
        "",
        "## Business Model & Segment Direction",
        *claim_lines("BUSINESS_MODEL"),
        "",
        "## Financial Trend Commentary",
        *claim_lines("FINANCIAL_TREND"),
        "",
        "## Promoter & Governance Observations",
        *claim_lines("PROMOTER_GOVERNANCE"),
        "",
        "## Key Contradictions & Data Quality Notes",
        *contradiction_lines,
        "",
        "## Verdict",
        f"**Label:** {verdict['verdict_label']}",
        "",
        verdict["verdict_summary"],
        "",
        "### Supporting points",
        *supporting_points,
        "",
        "### Risks / caveats",
        *risk_points,
    ]

    if include_appendix:
        report_lines += ["", "## Appendix: Evidence References"]
        if appendix_lines:
            report_lines += appendix_lines
        else:
            report_lines += ["- No evidence references available."]

    markdown = "\n".join(report_lines)
    citation_count = len(citation_map)

    existing = db.query(Report).filter(Report.run_id == run.id, Report.version == version).first()
    if existing:
        existing.verdict_label = verdict["verdict_label"]
        existing.verdict_summary = verdict["verdict_summary"]
        existing.report_markdown = markdown
        existing.citation_count = citation_count
        db.add(existing)
        db.commit()
        db.refresh(existing)
        saved = existing
    else:
        saved = Report(
            run_id=run.id,
            company_id=run.company_id,
            version=version,
            verdict_label=verdict["verdict_label"],
            verdict_summary=verdict["verdict_summary"],
            report_markdown=markdown,
            citation_count=citation_count,
        )
        db.add(saved)
        db.commit()
        db.refresh(saved)

    return {
        "runId": str(run.id),
        "version": saved.version,
        "verdictLabel": saved.verdict_label,
        "verdictSummary": saved.verdict_summary,
        "citationCount": int(saved.citation_count),
        "reportMarkdown": saved.report_markdown,
        "createdAt": saved.created_at,
    }