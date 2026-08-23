from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)


def test_week2_discover_sources_contract():
    # create run
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200, create_res.text
    run_id = create_res.json()["runId"]

    # discover
    discover_res = client.post(f"/research-runs/{run_id}/discover-sources")
    assert discover_res.status_code == 200, discover_res.text
    data = discover_res.json()

    assert "runId" in data
    assert data["runId"] == run_id
    assert "countsBySourceType" in data

    counts = data["countsBySourceType"]
    for k in ["NSE_ANNOUNCEMENT", "NSE_RESULTS", "BSE_FILING", "COMPANY_IR"]:
        assert k in counts

    # list endpoint should exist even if empty in isolated test DB state
    list_res = client.get(f"/research-runs/{run_id}/sources")
    assert list_res.status_code == 200, list_res.text
    assert isinstance(list_res.json(), list)