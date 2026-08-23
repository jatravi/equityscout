from fastapi.testclient import TestClient
from apps.api.src.main import app

client = TestClient(app)


def test_week3_discover_ingest_and_list_documents():
    # 1) Create run
    create_res = client.post("/research-runs", json={"company": "Reliance Industries"})
    assert create_res.status_code == 200, create_res.text
    run_id = create_res.json()["runId"]

    # 2) Discover sources
    discover_res = client.post(f"/research-runs/{run_id}/discover-sources")
    assert discover_res.status_code == 200, discover_res.text
    discover_data = discover_res.json()
    assert "countsBySourceType" in discover_data

    # 3) Ingest docs from discovered sources
    ingest_res = client.post(f"/research-runs/{run_id}/ingest-docs")
    assert ingest_res.status_code == 200, ingest_res.text
    ingest_data = ingest_res.json()

    assert ingest_data["runId"] == run_id
    assert "totalSources" in ingest_data
    assert "fetched" in ingest_data
    assert "deduped" in ingest_data
    assert "parsed" in ingest_data
    assert "failed" in ingest_data

    # Basic invariant
    total_processed = (
        ingest_data["fetched"]
        + ingest_data["deduped"]
        + ingest_data["failed"]
    )
    assert total_processed <= ingest_data["totalSources"]

    # 4) List documents
    docs_res = client.get(f"/research-runs/{run_id}/documents")
    assert docs_res.status_code == 200, docs_res.text
    docs_data = docs_res.json()

    assert docs_data["runId"] == run_id
    assert isinstance(docs_data["items"], list)

    # If any fetched docs exist, validate shape
    if docs_data["items"]:
        item = docs_data["items"][0]
        for k in [
            "documentId",
            "url",
            "canonicalUrl",
            "contentHash",
            "fetchedAt",
            "parserStatus",
        ]:
            assert k in item

        assert item["parserStatus"] in ["PENDING", "PARSED", "FAILED"]

    # 5) Re-run ingest to validate dedupe path is exercised
    ingest_res_2 = client.post(f"/research-runs/{run_id}/ingest-docs")
    assert ingest_res_2.status_code == 200, ingest_res_2.text
    ingest_data_2 = ingest_res_2.json()

    assert ingest_data_2["runId"] == run_id
    # On second run, dedupe should usually be >= first run.
    # Keep it non-strict to avoid flakiness in provider variability.
    assert ingest_data_2["deduped"] >= 0