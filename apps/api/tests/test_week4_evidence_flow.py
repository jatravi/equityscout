from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_week4_extract_and_list_evidence():
    # create run
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200, create_res.text
    run_id = create_res.json()["runId"]

    # discover + ingest (depends on week2/week3)
    d1 = client.post(f"/research-runs/{run_id}/discover-sources")
    assert d1.status_code == 200, d1.text

    d2 = client.post(f"/research-runs/{run_id}/ingest-docs")
    assert d2.status_code == 200, d2.text

    # extract evidence
    ex = client.post(f"/research-runs/{run_id}/extract-evidence")
    assert ex.status_code == 200, ex.text
    exj = ex.json()

    assert exj["runId"] == run_id
    assert "processedDocuments" in exj
    assert "extracted" in exj
    assert "countsByType" in exj

    # list evidence
    ev = client.get(f"/research-runs/{run_id}/evidence")
    assert ev.status_code == 200, ev.text
    evj = ev.json()
    assert evj["runId"] == run_id
    assert isinstance(evj["items"], list)

    # every row must have document locator
    for item in evj["items"]:
        assert item["documentId"]
        assert item["locator"] is not None
        assert isinstance(item["locator"], dict)