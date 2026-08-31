## EquityScout API

EquityScout is a staged research pipeline for equity analysis:
- **Week 1:** Run orchestration + report retrieval base
- **Week 2:** India company resolution + source discovery/ranking
- **Week 3:** Document retrieval, dedup, parsing, and persistence
- **Week 4:** Evidence extraction v1 (business, financial, promoter)

---

## Local setup

### 1) Create virtual environment + install deps

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Configure database

Set your Postgres connection (example):

```bash
# PowerShell
$env:DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/equityscouts"
```

### 3) Run DB migrations (required)

Apply all migration files in order:
- `infra/db/migrations/001_*.sql`
- `infra/db/migrations/002_*.sql`
- `infra/db/migrations/003_documents_dedup.sql`
- `infra/db/migrations/004_parsed_documents.sql`
- `infra/db/migrations/005_evidence_v1.sql`

> If using `gen_random_uuid()`, ensure:
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### 4) Start API

```bash
python -m uvicorn apps.api.src.main:app --reload
```

Open Swagger: `http://127.0.0.1:8000/docs`

---

## Week 2 API Flow (company resolution + source discovery)

### Create run
`POST /research-runs`

```json
{
  "company": "Reliance Industries"
}
```

### Discover sources
`POST /research-runs/{runId}/discover-sources`

What it does:
- resolves legal/alias/fuzzy match
- calls providers (NSE/BSE/IR)
- ranks sources (authority/relevance/freshness)
- upserts canonical source rows

### List ranked sources
`GET /research-runs/{runId}/sources`

Ordered by:
1. `rankScore` desc
2. `publishedAt` desc

### Optional resolver debug
`POST /companies/resolve`

```json
{
  "company": "RIL"
}
```

---

## Week 3 API Flow (retrieval + parsing base)

### Ingest documents
`POST /research-runs/{runId}/ingest-docs`

Pipeline:
1. fetch each discovered source URL
2. retry/backoff/rate-limit handling
3. canonicalize URL + compute SHA256
4. dedupe by `(company_id, canonical_url)` (and hash policy if enabled)
5. parse content (HTML/PDF)
6. persist:
   - raw row → `documents`
   - parsed row → `parsed_documents`

Response shape:

```json
{
  "runId": "uuid",
  "totalSources": 12,
  "fetched": 7,
  "deduped": 3,
  "parsed": 7,
  "failed": 2
}
```

### List ingested docs
`GET /research-runs/{runId}/documents`

Each item includes:
- `documentId`, `sourceId`
- `url`, `canonicalUrl`, `contentHash`
- `httpStatus`, `contentType`, `fetchedAt`
- `parserStatus` (`PENDING | PARSED | FAILED`)
- parsed fields (`parseTitle`, `parseLength`, `parseMetadata`)

---

## Week 4 API Flow (evidence extraction v1)

### Extract evidence
`POST /research-runs/{runId}/extract-evidence`

Runs extractors on parsed docs and persists rows into `evidence`.

Extractors included:
1. **Business summary signals**
   - capacity/expansion
   - order wins/contracts
   - capex mentions
   - guidance/outlook
   - regulatory/legal cues

2. **Financial metrics (basic set)**
   - revenue
   - net profit / PAT
   - operating/EBITDA margin
   - debt
   - operating cash flow

3. **Promoter/shareholding basics**
   - promoter holding %
   - pledge indicator mentions

Response shape:

```json
{
  "runId": "uuid",
  "processedDocuments": 8,
  "extracted": 27,
  "deduped": 5,
  "failedDocuments": 0,
  "countsByType": {
    "BUSINESS_SIGNAL": 10,
    "FINANCIAL_METRIC": 12,
    "PROMOTER_HOLDING": 5
  }
}
```

### List evidence
`GET /research-runs/{runId}/evidence`

Optional filter:
- `?evidence_type=BUSINESS_SIGNAL`
- `?evidence_type=FINANCIAL_METRIC`
- `?evidence_type=PROMOTER_HOLDING`

Each evidence row includes:
- `evidenceId`, `runId`, `companyId`, `documentId`
- `evidenceType`, `key`
- `valueText`, `valueNum`, `valueUnit`, `period`
- `confidence`
- `locator` (**required traceability field**)
- `snippet`, `createdAt`

---

## PowerShell quick run (Week 2 → Week 4)

```powershell
$body = @{ company = "Reliance Industries" } | ConvertTo-Json
$run = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs" `
  -ContentType "application/json" `
  -Body $body

$runId = $run.runId

# Week 2
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/discover-sources"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/sources"

# Week 3
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/ingest-docs"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/documents"

# Week 4
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/extract-evidence"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/evidence"
```

---

## Tests

Run staged flow tests:

```bash
pytest -q apps/api/tests/test_week1_flow.py
pytest -q apps/api/tests/test_week2_flow.py
pytest -q apps/api/tests/test_week3_flow.py
pytest -q apps/api/tests/test_week4_evidence_flow.py
```

Expected (current): all passing.

---

## Milestone checklists

### Week 2
- [x] Create run
- [x] Discover sources
- [x] Fetch ranked sources
- [x] Persist NSE/BSE/IR metadata

### Week 3
- [x] Ingest docs for discovered sources
- [x] Retry/backoff/429 handling
- [x] Canonical URL + hash dedupe
- [x] HTML + PDF parsing
- [x] Raw + parsed artifacts persisted/queryable

### Week 4
- [x] Business evidence extraction
- [x] Financial metrics extraction (basic set)
- [x] Promoter/shareholding extraction (basic)
- [x] Evidence persisted with required document locator
- [x] `/extract-evidence` and `/evidence` endpoints
```