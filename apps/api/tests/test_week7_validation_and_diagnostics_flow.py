from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_week7_validation_and_diagnostics_flow():
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200, create_res.text
    run_id = create_res.json()["runId"]

    assert client.post(f"/research-runs/{run_id}/discover-sources").status_code == 200
    assert client.post(f"/research-runs/{run_id}/ingest-docs").status_code == 200
    assert client.post(f"/research-runs/{run_id}/extract-evidence").status_code == 200
    assert client.post(f"/research-runs/{run_id}/build-claims").status_code == 200

    gen = client.post(f"/research-runs/{run_id}/generate-report?include_appendix=true")
    assert gen.status_code == 200, gen.text
    gj = gen.json()

    assert gj["runId"] == run_id
    assert gj["version"] == "v1"
    assert gj["validationStatus"] in ["VALID", "INVALID"]
    assert "validation" in gj
    assert "isValid" in gj["validation"]
    assert "uncitedClaimCount" in gj["validation"]

    # diagnostics endpoint
    d = client.get(f"/research-runs/{run_id}/diagnostics")
    assert d.status_code == 200, d.text
    dj = d.json()

    assert dj["runId"] == run_id
    assert "sourceSuccessRate" in dj
    assert "parserFailureRate" in dj
    assert "claimsCount" in dj
    assert "citationCount" in dj
    assert dj["reportValidationStatus"] in ["PENDING", "VALID", "INVALID"]