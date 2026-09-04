from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)

def test_week6_generate_and_get_report():
    # Week1..Week5 setup
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200, create_res.text
    run_id = create_res.json()["runId"]

    assert client.post(f"/research-runs/{run_id}/discover-sources").status_code == 200
    assert client.post(f"/research-runs/{run_id}/ingest-docs").status_code == 200
    assert client.post(f"/research-runs/{run_id}/extract-evidence").status_code == 200
    assert client.post(f"/research-runs/{run_id}/build-claims").status_code == 200

    # generate report
    gen = client.post(f"/research-runs/{run_id}/generate-report?include_appendix=true")
    assert gen.status_code == 200, gen.text
    gj = gen.json()

    assert gj["runId"] == run_id
    assert gj["version"] == "v1"
    assert gj["verdictLabel"] in ["POSITIVE", "MIXED", "CAUTIOUS"]
    assert isinstance(gj["reportMarkdown"], str)
    assert len(gj["reportMarkdown"]) > 50

    md = gj["reportMarkdown"]
    assert "## Business Model & Segment Direction" in md
    assert "## Financial Trend Commentary" in md
    assert "## Promoter & Governance Observations" in md
    assert "## Verdict" in md
    assert "## Appendix: Evidence References" in md

    # lightweight inline citation check
    if gj["citationCount"] > 0:
        assert "[E" in md
    else:
        assert "No evidence references available." in md

    # get report
    getr = client.get(f"/research-runs/{run_id}/report")
    assert getr.status_code == 200, getr.text
    rj = getr.json()

    assert rj["runId"] == run_id
    assert rj["version"] == "v1"
    assert isinstance(rj["reportMarkdown"], str)
    assert len(rj["reportMarkdown"]) > 50
    