from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_week5_build_and_list_claims():
    # Week1/2/3/4 setup flow
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200, create_res.text
    run_id = create_res.json()["runId"]

    d1 = client.post(f"/research-runs/{run_id}/discover-sources")
    assert d1.status_code == 200, d1.text

    d2 = client.post(f"/research-runs/{run_id}/ingest-docs")
    assert d2.status_code == 200, d2.text

    d3 = client.post(f"/research-runs/{run_id}/extract-evidence")
    assert d3.status_code == 200, d3.text

    # build claims
    b = client.post(f"/research-runs/{run_id}/build-claims")
    assert b.status_code == 200, b.text
    bj = b.json()

    assert bj["runId"] == run_id
    assert "totalClaims" in bj
    assert "countsByType" in bj
    assert "contradictionCounts" in bj
    assert "avgConfidence" in bj

    # list claims
    lc = client.get(f"/research-runs/{run_id}/claims")
    assert lc.status_code == 200, lc.text
    lcj = lc.json()
    assert lcj["runId"] == run_id
    assert isinstance(lcj["items"], list)

    for item in lcj["items"]:
        assert item["supportingEvidenceCount"] >= 1
        assert isinstance(item["supportingLocators"], list)
        assert 0.0 <= float(item["confidence"]) <= 1.0