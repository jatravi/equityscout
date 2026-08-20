# Requirements (MVP)

## 1) Project Objective

Build an evidence-first deep-research equity analysis system that researches a listed company and generates a comprehensive, citation-backed Markdown investment research report.

- **MVP market scope:** Indian listed equities only.
- **Architecture constraint:** India-first implementation, but extensible for future US support without rewriting the core pipeline.

---

## 2) Scope Definition

## 2.1 In-Scope (MVP)

The system must research and synthesize:

1. **Business**
2. **Financials**
3. **Management / Promoters**

The system must produce a final report with required sections (see Section 8).

## 2.2 Out-of-Scope (MVP)

The following are explicitly not MVP requirements unless re-approved:

- US equity workflows
- Valuation frameworks (e.g., DCF, comparables)
- Peer comparison engine
- Price/technical analysis
- Prediction/forecasting
- Portfolio-level analytics
- Complex multi-agent hierarchies and distributed microservices

---

## 3) Functional Requirements

## 3.1 Company Input and Resolution

- Accept company input (e.g., name/symbol).
- Resolve to a single target Indian listed entity where possible.
- Preserve mapping metadata (e.g., symbol/code/identifier aliases).
- If resolution is ambiguous, system must mark ambiguity and avoid false attribution.

## 3.2 Research Areas

### A. Business

System should collect evidence relevant to:

- Business model
- Products/services
- Business/operating segments
- Markets served
- Customer exposure (where available)
- Competition and industry context
- Competitive advantages / moat indicators
- Growth drivers
- Business risks

### B. Financials

System should collect evidence relevant to:

- Revenue, profit, margins
- Cash flow
- Balance sheet, debt
- Capex
- Ratios (where derivable from reliable inputs)
- Historical trends (window configurable; not hardcoded to one fixed period)
- Current financial position
- Relevant annual reports, financial results, AGM and investor communications (as available)

### C. Management / Promoters

System should collect evidence relevant to:

- Background and experience
- Track record / execution signals
- Shareholding and promoter holding/pledging
- Related-party disclosures (where available)
- Management changes
- Governance/regulatory concerns
- Material controversies/litigation (only when evidenced)
- Credibility-related signals grounded in sources

---

## 4) Research Workflow Requirements

The system must use a structured pipeline (not a single LLM prompt):

```text
User Input
    ↓
Company Resolution
    ↓
Research Planner / Orchestrator
    ↓
Research Tasks (Business / Financials / Promoters)
    ↓
Source Discovery + Selection
    ↓
Document Retrieval
    ↓
Parsing + Extraction
    ↓
Evidence Store (+ Citation Metadata)
    ↓
Analysis (Claims)
    ↓
Investment Verdict
    ↓
Report Generation
    ↓
Claim/Citation Validation
    ↓
Final Markdown Report
```

- Independent tasks should be executable in parallel where safe and beneficial.
- Concurrency must be controlled based on provider limits and budget constraints.

---

## 5) Evidence, Citation, and Source Requirements

## 5.1 Evidence-First Principle

- Important report claims must be traceable to source evidence.
- LLM-generated text is **not evidence** unless linked to retrieved source-backed extraction.
- The system must preserve separation between:
  1. Sourced facts (evidence)
  2. Analytical interpretation (claims)
  3. Investment conclusion (verdict)

## 5.2 Source Priority

The system should prioritize authoritative sources, including:

- SEBI
- NSE
- BSE
- Company investor-relations pages and official disclosures
- Annual reports
- Financial results
- Investor presentations
- AGM-related disclosures
- Investor/earnings communication records (as available)
- Other regulatory disclosures

## 5.3 Citation Integrity

- System must store citation metadata through the pipeline (not add citations only at final formatting).
- Citations must not be fabricated.
- If evidence is insufficient, report must explicitly state limitation.

---

## 6) Efficiency and Reliability Requirements

## 6.1 Efficiency

System should minimize:

- Duplicate source discovery/search
- Duplicate document retrieval
- Duplicate document parsing/extraction
- Duplicate LLM calls
- Excessive prompt context
- Unbounded research loops

System should support (MVP baseline or staged rollout):

- Caching
- Deduplication (URL/content-level)
- Research state persistence
- Cost/token tracking
- Retry/fallback handling

## 6.2 Stopping / Budget Control

- Orchestration must support configurable budget/caps (time/cost/calls/depth).
- Stopping condition should allow early stop when sufficient evidence coverage is reached.
- Exact sufficiency strategy is configurable and can evolve post-MVP.

## 6.3 Failure Handling

System must gracefully handle:

- Broken/unavailable links
- Partial source coverage
- Parsing failures
- Rate limits/timeouts
- Conflicting data points
- LLM/tool failures

The run log should capture failures, retries, skips, and final coverage status.

---

## 7) Investment Verdict Requirements

- Final report must include an **Investment Verdict** section.
- Verdict framework must be pluggable/replaceable.
- MVP must **not** hardcode a rigid scoring system unless explicitly approved.
- Verdict should be grounded in evidence-backed analysis and acknowledge uncertainty where applicable.

---

## 8) Final Report Requirements (Markdown)

MVP output must include at least:

1. Business Overview
2. Investment Verdict
3. Moat
4. Financial Summary
5. Relevant Historical Financial Information
6. AGM / Investor Communication Highlights (where available)
7. Promoter and Management Deep Dive

Additional report rules:

- Important claims should include citations.
- Missing/unverified information must be clearly indicated.
- Report should avoid unsupported positive/negative assertions.

---

## 9) Non-Functional Requirements

Priority order:

1. Correctness
2. Evidence traceability
3. Reliability under partial failure
4. Modularity and maintainability
5. Cost efficiency
6. Execution time
7. Scalability/extensibility

Additional NFR expectations:

- Reproducible research runs (same inputs should produce auditable run artifacts)
- Observability for run status, source usage, failures, and model usage

---

## 10) Acceptance Criteria (MVP Gate)

A research run is MVP-acceptable only if all are true:

1. Report includes all required sections (Section 8).
2. Major analytical claims are citation-backed.
3. Citation links point to retrievable source artifacts with locator metadata where feasible.
4. Unsupported claims are not presented as facts.
5. Missing data is explicitly disclosed.
6. Run records include enough diagnostics to audit how conclusions were formed.

---

## 11) Future Compatibility (Post-MVP)

Architecture should remain compatible with future additions:

- US equities
- Additional data providers
- Valuation modules
- Peer comparison
- Price/technical analysis
- Prediction/forecasting
- Portfolio-level analysis

These are explicitly deferred and not MVP delivery blockers.