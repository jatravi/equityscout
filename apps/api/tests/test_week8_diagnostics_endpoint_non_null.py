from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_diagnostics_endpoint_has_non_null_schema():
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200
    run_id = create_res.json()["runId"]

    assert client.post(f"/research-runs/{run_id}/discover-sources").status_code == 200
    assert client.post(f"/research-runs/{run_id}/ingest-docs").status_code == 200
    assert client.post(f"/research-runs/{run_id}/extract-evidence").status_code == 200
    assert client.post(f"/research-runs/{run_id}/build-claims").status_code == 200
    assert client.post(f"/research-runs/{run_id}/generate-report?include_appendix=true").status_code == 200

    d = client.get(f"/research-runs/{run_id}/diagnostics")
    assert d.status_code == 200, d.text
    j = d.json()

    required = [
        "runId", "sourcesTotal", "sourcesSuccess", "sourceSuccessRate",
        "docsTotal", "docsParsed", "parserFailureRate",
        "evidenceCount", "claimsCount", "citationCount",
        "reportValidationStatus", "validationErrorCount",
        "discoverMs", "ingestMs", "extractMs", "claimsMs", "reportMs",
        "tokenInput", "tokenOutput", "estimatedCost"
    ]
    for k in required:
        assert k in j
        assert j[k] is not None