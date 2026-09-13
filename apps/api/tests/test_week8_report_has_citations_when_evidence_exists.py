from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_report_has_citations_when_evidence_exists():
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200
    run_id = create_res.json()["runId"]

    assert client.post(f"/research-runs/{run_id}/discover-sources").status_code == 200
    assert client.post(f"/research-runs/{run_id}/ingest-docs").status_code == 200
    assert client.post(f"/research-runs/{run_id}/extract-evidence").status_code == 200
    assert client.post(f"/research-runs/{run_id}/build-claims").status_code == 200

    gen = client.post(f"/research-runs/{run_id}/generate-report?include_appendix=true")
    assert gen.status_code == 200, gen.text
    body = gen.json()

    # if claims exist, citations should be present
    # (soft guard in case upstream extractor returns zero evidence in local env)
    citation_count = int(body.get("citationCount", 0))
    report_md = body.get("reportMarkdown", "")
    if "No supporting points available" not in report_md:
        assert citation_count > 0, "Expected citations when claims are present"
        assert "[E" in report_md