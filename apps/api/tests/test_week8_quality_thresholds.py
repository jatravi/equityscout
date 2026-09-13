from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_week8_single_run_quality_fields_present():
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

    assert "validationStatus" in gj
    assert "validation" in gj

    diag = client.get(f"/research-runs/{run_id}/diagnostics")
    assert diag.status_code == 200, diag.text
    dj = diag.json()

    # Week 8 QA metrics
    for key in [
        "sourceSuccessRate",
        "parserFailureRate",
        "estimatedCost",
        "claimsCount",
        "citationCount",
        "reportValidationStatus",
        "validationErrorCount",
    ]:
        assert key in dj, f"missing {key}"