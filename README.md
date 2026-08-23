## Week 2 API Flow (India company resolution + source discovery)

This flow validates:
1. Company resolution (legal name / alias / fuzzy alias)
2. Source discovery from NSE/BSE/IR providers
3. Authority + relevance + freshness ranking
4. Ranked source retrieval for a research run

### 1) Create a research run

`POST /research-runs`

Request:
```json
{
  "company": "Reliance Industries"
}
```

Response (example):
```json
{
  "runId": "13e904c2-79d8-4420-a654-6c68f23293ee",
  "status": "PENDING",
  "company": "Reliance Industries"
}
```

---

### 2) Discover sources for a run

`POST /research-runs/{runId}/discover-sources`

What it does:
- resolves company (NSE/BSE symbol/code + alias/fuzzy matching),
- invokes providers (NSE announcements/results, BSE filings, IR page),
- ranks sources,
- persists canonical source rows using upsert semantics.

Response (example):
```json
{
  "runId": "13e904c2-79d8-4420-a654-6c68f23293ee",
  "company": "Reliance Industries",
  "resolvedMatchType": "EXACT_LEGAL_NAME",
  "totalDiscovered": 4,
  "totalUpdated": 8,
  "countsBySourceType": {
    "NSE_ANNOUNCEMENT": 3,
    "NSE_RESULTS": 3,
    "BSE_FILING": 3,
    "COMPANY_IR": 3
  }
}
```

> Note: Duplicate provider URLs across BUSINESS / FINANCIAL / PROMOTER tasks are deduplicated at DB layer using canonical uniqueness.

---

### 3) Fetch ranked sources for a run

`GET /research-runs/{runId}/sources`

Returns ranked source list ordered by:
1. `rankScore` (descending)
2. `publishedAt` (descending)

Each source includes:
- `sourceType`
- `authorityScore`
- `rankScore`
- `url`
- `publisher`
- `publishedAt`

---

### 4) Optional: debug resolver quality

`POST /companies/resolve`

Request:
```json
{
  "company": "RIL"
}
```

Response (example):
```json
{
  "companyId": "...",
  "legalName": "Reliance Industries",
  "nseSymbol": "RELIANCE",
  "bseCode": "500325",
  "matchedAlias": "RIL",
  "confidence": 0.99,
  "matchType": "EXACT_ALIAS"
}
```

---

### PowerShell quick run

```powershell
$body = @{ company = "Reliance Industries" } | ConvertTo-Json
$run = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs" `
  -ContentType "application/json" `
  -Body $body

$runId = $run.runId

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/discover-sources"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/sources"
```

---

### Week 2 done criteria checklist

- [x] Create run (`POST /research-runs`)
- [x] Discover sources (`POST /research-runs/{id}/discover-sources`)
- [x] Fetch ranked sources (`GET /research-runs/{id}/sources`)
- [x] Persist NSE/BSE/IR metadata in DB