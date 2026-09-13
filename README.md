## EquityScout API

EquityScout is a staged research pipeline for equity analysis:
- **Week 1:** Run orchestration + report retrieval base
- **Week 2:** India company resolution + source discovery/ranking
- **Week 3:** Document retrieval, dedup, parsing, and persistence
- **Week 4:** Evidence extraction v1 (business, financial, promoter)
- **Week 5:** Claims analysis v1 (business/financial/promoter + contradictions + confidence)
- **Week 6:** VerdictStrategy v1 + fixed-format report generation with inline citations
- **Week 7:** Validation + reliability hardening (claim-citation validation + diagnostics)
- **Week 8:** QA + benchmark automation (cohort runs, regression pack, freeze readiness)

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
- `infra/db/migrations/008_run_diagnostics_and_report_validation.sql`

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

### List evidence
`GET /research-runs/{runId}/evidence`

Optional filter:
- `?evidence_type=BUSINESS_SIGNAL`
- `?evidence_type=FINANCIAL_METRIC`
- `?evidence_type=PROMOTER_HOLDING`

---

## Week 5 API Flow (claims analysis v1)

### Build claims
`POST /research-runs/{runId}/build-claims`

Generates claims from extracted evidence and persists rows into `claims`.

### List claims
`GET /research-runs/{runId}/claims`

Optional filters:
- `?claim_type=BUSINESS_MODEL|FINANCIAL_TREND|PROMOTER_GOVERNANCE`
- `?min_confidence=0.6`
- `?contradiction_tag=NONE|INTRA_DOC|CROSS_DOC|METRIC_CONFLICT`

---

## Week 6 API Flow (verdict + report generation v1)

### Generate report
`POST /research-runs/{runId}/generate-report`

Optional query params:
- `include_appendix=true|false` (default `true`)
- `min_confidence=<float>`

### Get latest report
`GET /research-runs/{runId}/report`

---

## Week 7 API Flow (validation + diagnostics)

### Report validation behavior
`POST /research-runs/{runId}/generate-report`

Week 7 adds:
- key-claim citation validation
- graceful degradation messages for low/no evidence
- validation payload in response

Additional response fields:
- `validationStatus`: `VALID | INVALID | PENDING`
- `validation`:
  - `isValid`
  - `uncitedClaimCount`
  - `errors[]`

### Run diagnostics
`GET /research-runs/{runId}/diagnostics`

Returns per-run reliability/quality metrics:
- token/cost snapshot:
  - `tokenInput`, `tokenOutput`, `estimatedCost`
- source reliability:
  - `sourcesTotal`, `sourcesSuccess`, `sourceSuccessRate`
- parser reliability:
  - `docsTotal`, `docsParsed`, `parserFailureRate`
- output quality:
  - `evidenceCount`, `claimsCount`, `citationCount`
  - `reportValidationStatus`, `validationErrorCount`
- timing:
  - `discoverMs`, `ingestMs`, `extractMs`, `claimsMs`, `reportMs`

---

## Week 8 — QA + benchmark runs

### Benchmark runner
Run multi-company benchmark (10–20 Indian companies mix):

```bash
python scripts/run_week8_benchmark.py \
  --base-url http://127.0.0.1:8000 \
  --companies-file apps/api/tests/fixtures/week8_companies.json \
  --max-companies 12 \
  --stage-timeout 120 \
  --out-dir artifacts/week8
```

### Week 8 reliability hardening in runner
- hard per-stage timeout (`--stage-timeout`)
- continue-on-failure/timeout across remaining companies
- interim checkpoint JSON written after each company
- `KeyboardInterrupt` handling writes partial/final summary
- Windows-safe console output (`[OK]`, `[FAIL]`)

### Benchmark artifacts
- `artifacts/week8/week8_benchmark_YYYYMMDD_HHMMSS.partial.json`
- `artifacts/week8/week8_benchmark_YYYYMMDD_HHMMSS.json`
- `artifacts/week8/week8_benchmark_YYYYMMDD_HHMMSS.md`

### Metrics tracked
- citation coverage proxy (`citationCount`, validation errors)
- unsupported claim rate proxy (`validationErrorCount / claimsCount`)
- runtime (stage elapsed ms aggregate)
- estimated cost (`estimatedCost`)
- source success rate (`sourceSuccessRate`)
- parser failure rate (`parserFailureRate`)

### Week 8 tests
```bash
pytest -q apps/api/tests/test_week8_benchmark_smoke.py
pytest -q apps/api/tests/test_week8_quality_thresholds.py
pytest -q apps/api/tests/test_week8_citation_pipeline.py
pytest -q apps/api/tests/test_week8_diagnostics_math.py
pytest -q apps/api/tests/test_week8_diagnostics_endpoint_non_null.py
pytest -q apps/api/tests/test_week8_regressions.py
```

---

## PowerShell quick run (Week 2 → Week 7)

```powershell
$body = @{ company = "Reliance Industries" } | ConvertTo-Json
$run = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/research-runs" `
  -ContentType "application/json" `
  -Body $body

$runId = $run.runId

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/research-runs/$runId/discover-sources"
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/research-runs/$runId/ingest-docs"
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/research-runs/$runId/extract-evidence"
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/research-runs/$runId/build-claims"
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/research-runs/$runId/generate-report?include_appendix=true"
Invoke-RestMethod -Method GET  -Uri "http://127.0.0.1:8000/research-runs/$runId/report"
Invoke-RestMethod -Method GET  -Uri "http://127.0.0.1:8000/research-runs/$runId/diagnostics"
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
pytest -q apps/api/tests/test_week6_report_flow.py
pytest -q apps/api/tests/test_week7_validation_and_diagnostics_flow.py
```

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
- [x] Evidence extraction and persistence
- [x] `/extract-evidence` and `/evidence` endpoints

### Week 5
- [x] Claims built from evidence
- [x] Contradiction tagging + confidence scoring
- [x] `/build-claims` and `/claims` endpoints
- [x] End-to-end Week 5 flow test

### Week 6
- [x] VerdictStrategy v1
- [x] Fixed-format report with inline citations
- [x] `/generate-report` and `/report` endpoints
- [x] End-to-end Week 6 flow test

### Week 7
- [x] Claim-citation validator
- [x] Graceful degradation messaging
- [x] Diagnostics endpoint (`/research-runs/{runId}/diagnostics`)
- [x] Validation + diagnostics flow test

### Week 8
- [x] Benchmark cohort fixture (`week8_companies.json`)
- [x] Benchmark runner (`run_week8_benchmark.py`)
- [x] Runner timeout/checkpoint/interrupt hardening
- [x] Citation pipeline regression guards
- [x] Diagnostics hardening regression guards
- [x] Week 8 regression pack (`test_week8_regressions.py`)
- [ ] Final 10–20 cohort freeze signoff against acceptance thresholds