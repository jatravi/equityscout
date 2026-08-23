from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)


def test_week1_create_run_success():
    res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert res.status_code == 200, res.text
    data = res.json()

    assert "runId" in data
    assert data["company"] == "Reliance Industries"
    assert "status" in data