## EquityScout API

EquityScout is a staged research pipeline for equity analysis:
- **Week 1:** Run orchestration + report retrieval base
- **Week 2:** India company resolution + source discovery/ranking
- **Week 3:** Document retrieval, dedup, parsing, and persistence
- **Week 4:** Evidence extraction v1 (business, financial, promoter)
- **Week 5:** Claims analysis v1 (business/financial/promoter + contradictions + confidence)
- **Week 6:** VerdictStrategy v1 + fixed-format report generation with inline citations

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
- `infra/db/migrations/006_claims_v1.sql`
- `infra/db/migrations/007_reports_v1.sql`

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

## Week 5 API Flow (claims analysis v1)

### Build claims
`POST /research-runs/{runId}/build-claims`

Generates claims from extracted evidence and persists rows into `claims`.

Claim categories:
1. **Business model + segment direction** (`BUSINESS_MODEL`)
2. **Financial trend commentary** (`FINANCIAL_TREND`)
3. **Promoter/governance observations** (`PROMOTER_GOVERNANCE`)

Also performs:
- contradiction tagging (`NONE`, `INTRA_DOC`, `CROSS_DOC`, `METRIC_CONFLICT`)
- deterministic confidence scoring (`0.0–1.0`)

Response shape:

```json
{
  "runId": "uuid",
  "totalClaims": 14,
  "countsByType": {
    "BUSINESS_MODEL": 4,
    "FINANCIAL_TREND": 7,
    "PROMOTER_GOVERNANCE": 3
  },
  "contradictionCounts": {
    "NONE": 11,
    "INTRA_DOC": 0,
    "CROSS_DOC": 1,
    "METRIC_CONFLICT": 2
  },
  "avgConfidence": 0.67
}
```

### List claims
`GET /research-runs/{runId}/claims`

Optional filters:
- `?claim_type=BUSINESS_MODEL|FINANCIAL_TREND|PROMOTER_GOVERNANCE`
- `?min_confidence=0.6`
- `?contradiction_tag=NONE|INTRA_DOC|CROSS_DOC|METRIC_CONFLICT`

Each claim row includes:
- `claimId`, `runId`, `companyId`
- `claimType`, `claimText`, `stance`
- `confidence`
- `contradictionTag`, `contradictionNote`
- `supportingEvidenceCount`
- `supportingLocators`
- `createdAt`

---

<<<<<<< HEAD
## PowerShell quick run (Week 2 → Week 5)
=======
>>>>>>> 0e04efcdd46e640ac289bda365be6de9ad6f7b27
## Week 6 API Flow (verdict + report generation v1)

### Generate report
`POST /research-runs/{runId}/generate-report`

Builds a narrative verdict and fixed-format markdown report from Week 5 claims (+ evidence references), then persists to `reports`.

Optional query params:
- `include_appendix=true|false` (default `true`)
- `min_confidence=<float>`

Response shape:

```json
{
  "runId": "uuid",
  "version": "v1",
  "verdictLabel": "MIXED",
  "verdictSummary": "Overall view is mixed based on supported claims...",
  "citationCount": 12,
  "reportMarkdown": "# EquityScout Research Report ...",
  "createdAt": "2026-08-31T00:00:00Z"
}
```

### Get latest report
`GET /research-runs/{runId}/report`

Returns latest persisted v1 report for the run.

Response shape:

```json
{
  "runId": "uuid",
  "version": "v1",
  "verdictLabel": "MIXED",
  "verdictSummary": "Overall view is mixed based on supported claims...",
  "citationCount": 12,
  "reportMarkdown": "# EquityScout Research Report ...",
  "createdAt": "2026-08-31T00:00:00Z"
}
```

### Fixed report sections (MVP)
Generated markdown includes:

1. `# EquityScout Research Report`
2. `## Company Snapshot`
3. `## Business Model & Segment Direction`
4. `## Financial Trend Commentary`
5. `## Promoter & Governance Observations`
6. `## Key Contradictions & Data Quality Notes`
7. `## Verdict`
8. `## Appendix: Evidence References` (when `include_appendix=true`)

### Citation format
- Inline markers in narrative: `[E1]`, `[E2]`, ...
- Appendix mapping:
  - `[E1] <title/key> — <canonical_url> (snippet: "...")`

---

## PowerShell quick run (Week 2 → Week 6)

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

# Week 5
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/build-claims"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/claims"

# Week 6
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/generate-report?include_appendix=true"

Invoke-RestMethod -Method GET `
  -Uri "http://127.0.0.1:8000/research-runs/$runId/report"
```

---

## Tests

Run staged flow tests:

```bash
pytest -q apps/api/tests/test_week1_flow.py
pytest -q apps/api/tests/test_week2_flow.py
pytest -q apps/api/tests/test_week3_flow.py
pytest -q apps/api/tests/test_week4_evidence_flow.py
pytest -q apps/api/tests/test_week5_claims_flow.py
<<<<<<< HEAD
```

Expected (current): all passing for Week 1–5 flow.

pytest -q apps/api/tests/test_week6_report_flow.py
```

=======
pytest -q apps/api/tests/test_week6_report_flow.py
```

>>>>>>> 0e04efcdd46e640ac289bda365be6de9ad6f7b27
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

### Week 5
- [x] Claims built from Week 4 evidence
- [x] Business/financial/promoter claim categories
- [x] Contradiction tagging
- [x] Confidence scoring
- [x] `/build-claims` and `/claims` endpoints
- [x] End-to-end Week 5 flow test
- [x] End-to-end Week 5 flow test

### Week 6
- [x] VerdictStrategy v1 (narrative-first)
- [x] Fixed MVP report sections
- [x] Inline citation markers in markdown
- [x] Appendix evidence reference mapping
- [x] `/generate-report` and `/report` endpoints
- [x] End-to-end Week 6 flow test
- [x] End-to-end Week 6 flow test
