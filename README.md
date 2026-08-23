## Week 3 API Flow (retrieval + parsing base)

### Endpoints
- `POST /research-runs/{runId}/ingest-docs`
- `GET /research-runs/{runId}/documents`

### What Week 3 adds
- Fetcher with timeout + retry + exponential backoff (+ 429 handling)
- Dedup via canonical URL + SHA256 content hash
- Parser dispatcher with HTML + PDF support
- Persistence of raw (`documents`) and parsed (`parsed_documents`) artifacts

### Quick run

```powershell
$body = @{ company = "Reliance Industries" } | ConvertTo-Json
$run = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs" `
  -ContentType "application/json" `
  -Body $body
$runId = $run.runId

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/discover-sources"

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/ingest-docs"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/documents"
```

### Done criteria (Week 3)
- [x] Can ingest docs for discovered sources
- [x] Handles transient failures (retry/backoff/429)
- [x] Duplicate URLs/content not reprocessed
- [x] PDF + HTML parsed to text
- [x] Raw + parsed artifacts persisted and queryable
