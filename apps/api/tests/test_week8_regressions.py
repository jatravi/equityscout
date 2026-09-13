import re
from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)


def _run_pipeline(company: str = "Reliance Industries") -> tuple[str, dict]:
    create = client.post("/research-runs", json={"company": company})
    assert create.status_code == 200, create.text
    run_id = create.json()["runId"]

    for step in ["discover-sources", "ingest-docs", "extract-evidence", "build-claims"]:
        res = client.post(f"/research-runs/{run_id}/{step}")
        assert res.status_code == 200, f"{step} failed: {res.text}"

    gen = client.post(f"/research-runs/{run_id}/generate-report?include_appendix=true")
    assert gen.status_code == 200, gen.text
    return run_id, gen.json()


def test_regression_citation_marker_count_matches_report_field():
    """
    Bucket: citation missing despite evidence available
    Guard: citationCount should match inline [E#] markers in markdown.
    """
    _, report = _run_pipeline()
    md = report.get("reportMarkdown", "") or ""
    inline_count = len(re.findall(r"\[E\d+\]", md))
    api_count = int(report.get("citationCount", 0) or 0)
    assert inline_count == api_count, (
        f"citationCount mismatch: inline={inline_count}, api={api_count}"
    )


def test_regression_low_evidence_fallback_appendix_present():
    """
    Bucket: low-evidence report rendering consistency
    Guard: appendix section always exists and has deterministic fallback text when no refs.
    """
    _, report = _run_pipeline()
    md = report.get("reportMarkdown", "") or ""
    assert "## Appendix: Evidence References" in md, "Appendix header missing"

    inline_count = len(re.findall(r"\[E\d+\]", md))
    if inline_count == 0:
        assert "No evidence references available." in md, (
            "Expected deterministic no-evidence fallback text"
        )


def test_regression_diagnostics_consistent_with_report_counts():
    """
    Bucket: diagnostics mismatch vs persisted state
    Guard: diagnostics citation/claims fields should not contradict report payload.
    """
    run_id, report = _run_pipeline()

    d = client.get(f"/research-runs/{run_id}/diagnostics")
    assert d.status_code == 200, d.text
    diag = d.json()

    report_citations = int(report.get("citationCount", 0) or 0)
    diag_citations = int(diag.get("citationCount", 0) or 0)
    assert diag_citations == report_citations, (
        f"Diagnostics/report citation mismatch: diag={diag_citations}, report={report_citations}"
    )

    claims = int(diag.get("claimsCount", 0) or 0)
    val_err = int(diag.get("validationErrorCount", 0) or 0)
    assert val_err <= max(claims, 0), (
        f"validationErrorCount ({val_err}) cannot exceed claimsCount ({claims})"
    )


def test_regression_parser_partial_failure_math_bounds():
    """
    Bucket: parser partial failure path handling
    Guard: parserFailureRate is always bounded [0,1] and mathematically coherent.
    """
    run_id, _ = _run_pipeline()

    d = client.get(f"/research-runs/{run_id}/diagnostics")
    assert d.status_code == 200, d.text
    diag = d.json()

    docs_total = int(diag.get("docsTotal", 0) or 0)
    docs_parsed = int(diag.get("docsParsed", 0) or 0)
    pfr = float(diag.get("parserFailureRate", 0.0) or 0.0)

    assert 0.0 <= pfr <= 1.0, f"parserFailureRate out of bounds: {pfr}"
    if docs_total > 0:
        expected = max(docs_total - docs_parsed, 0) / docs_total
        assert abs(pfr - expected) < 1e-4, (
            f"parserFailureRate mismatch: expected={expected}, got={pfr}"
        )


def test_regression_contradiction_confidence_contract():
    """
    Bucket: contradiction/claim confidence edge cases
    Guard: verdict remains in strict enum and validation status remains present.
    """
    _, report = _run_pipeline()

    assert report.get("verdictLabel") in {"POSITIVE", "MIXED", "CAUTIOUS"}, (
        f"Unexpected verdictLabel: {report.get('verdictLabel')}"
    )
    assert "validationStatus" in report, "Missing validationStatus in report payload"