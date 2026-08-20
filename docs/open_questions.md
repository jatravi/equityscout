# Open Questions (Decision Log Backlog)

> These questions require explicit decisions before architecture hardening.  
> Primary reviewer: **Vinit Bhaiya**  
> Status legend: `OPEN` | `DECIDED` | `DEFERRED`

---

## OQ-01: Research Stopping Condition

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** How does the orchestrator determine “enough evidence” for a pillar?
- **Why it matters:** Controls quality, cost, latency, and risk of over/under-research.
- **Options:**
  1. Fixed source/document count
  2. Required question coverage
  3. Evidence sufficiency scoring
  4. Budget/time cap only
  5. Hybrid (coverage + quality + budget)
- **Recommended starting point:** **Hybrid**
  - Minimum required question coverage per pillar
  - Minimum evidence quality threshold
  - Hard caps (time/tokens/docs/cost)
- **Owner:** Vinit + Engineering
- **Target decision by:** Before extractor/analysis freeze

---

## OQ-02: Research Budget Policy

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** What hard/soft budget limits should apply per run?
- **Why it matters:** Prevents runaway costs and unstable runtime.
- **Possible controls:**
  - Max LLM calls
  - Max search/retrieval calls
  - Max documents fetched/parsed
  - Max tokens
  - Max API cost
  - Max execution time
- **Recommended starting point:**
  - Enforce hard limits on **time + tokens + documents**
  - Log estimated cost per stage
  - Optional soft warnings before hard stop
- **Owner:** Engineering
- **Target decision by:** Before first end-to-end benchmark run

---

## OQ-03: Model Routing Strategy

- **Status:** OPEN
- **Priority:** MEDIUM
- **Decision needed:** Single model for MVP or multi-model routing from day 1?
- **Why it matters:** Impacts complexity, observability, and iteration speed.
- **Options:**
  1. Single-model MVP
  2. Multi-model (small model for extraction, strong model for synthesis)
- **Recommended starting point:** **Single-model MVP**, keep routing interfaces ready.
- **Owner:** Engineering
- **Target decision by:** Before LLM adapter finalization

---

## OQ-04: Parallelism Policy

- **Status:** OPEN
- **Priority:** MEDIUM
- **Decision needed:** Which tasks run in parallel and with what limits?
- **Why it matters:** Impacts throughput, provider rate limits, and failure amplification.
- **Initial candidate parallel tasks:**
  - Business
  - Financials
  - Management/Promoters
- **Recommended starting point:**
  - Parallelize pillar-level tasks
  - Serialize provider-heavy steps if rate-limited
  - Add provider-specific concurrency caps
- **Owner:** Engineering
- **Target decision by:** Before queue/orchestrator concurrency implementation

---

## OQ-05: Investment Verdict Framework

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** What should the verdict format and logic be for MVP?
- **Why it matters:** Core product output; high risk of overconfident unsupported conclusions.
- **Options:**
  1. Narrative verdict (no rigid score)
  2. Criteria-based rubric (qualitative bands)
  3. Numeric scoring framework
- **Recommended starting point:** **Narrative + explicit confidence + evidence limits** (pluggable strategy).
- **Owner:** Vinit + Product + Engineering
- **Target decision by:** Before report template freeze

---

## OQ-06: Historical Financial Depth

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** Default historical window for financial trend analysis?
- **Why it matters:** Changes retrieval volume and quality of trend conclusions.
- **Options:**
  1. Fixed 3 years
  2. Fixed 5 years
  3. Dynamic by data availability and question
- **Recommended starting point:** **Default baseline + dynamic extension**
  - Baseline window (e.g., 3 years)
  - Expand when evidence is insufficient for trend claims
- **Owner:** Product + Engineering
- **Target decision by:** Before financial extractor rules finalize

---

## OQ-07: Citation Granularity Standard

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** Minimum citation granularity required for “major claims.”
- **Why it matters:** Directly affects trust, auditability, and hallucination containment.
- **Options:**
  1. URL only
  2. Document + date
  3. Document + page/section
  4. Evidence-ID linked to claim + locator
- **Recommended starting point:** **Document + locator (page/section where feasible) + source metadata**.
- **Owner:** Engineering
- **Target decision by:** Before report validator implementation

---

## OQ-08: MVP Evaluation Framework

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** What metrics define MVP pass/fail?
- **Why it matters:** Prevents subjective shipping decisions.
- **Candidate metrics:**
  - Citation correctness rate
  - Major-claim citation coverage
  - Unsupported-claim rate
  - Financial fact accuracy
  - Source authority mix
  - Runtime per run
  - Cost per run
  - Human review score
- **Recommended starting point:** Define 5–7 gating metrics with thresholds.
- **Owner:** Product + Engineering
- **Target decision by:** Before pilot batch evaluation

---

## OQ-09: Initial Search/Retrieval Providers

- **Status:** OPEN
- **Priority:** MEDIUM
- **Decision needed:** Which concrete providers for first implementation?
- **Why it matters:** Determines reliability and integration complexity.
- **Expected MVP priority:** NSE, BSE, SEBI, company IR disclosures.
- **Recommended starting point:** Implement provider abstraction + start with 1–2 highest reliability providers first, then expand.
- **Owner:** Engineering
- **Target decision by:** Before source discovery milestone completion

---

## OQ-10: MVP “Definition of Demonstrable End-to-End”

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** What exact V1 flow and output quality qualifies as complete?
- **Proposed minimum flow:**
```text
Company Input
    ↓
Company Resolution
    ↓
Research Planning
    ↓
Source Discovery + Retrieval
    ↓
Parsing + Evidence Extraction
    ↓
Analysis
    ↓
Verdict
    ↓
Claim/Citation Validation
    ↓
Markdown Report
```
- **Proposed acceptance baseline:**
  1. Required report sections present
  2. Major claims citation-backed
  3. Missing evidence explicitly disclosed
  4. Run diagnostics available
- **Owner:** Vinit + Product + Engineering
- **Target decision by:** Before MVP completion sign-off

---

## OQ-11: Conflict Resolution Policy (New)

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** How to resolve conflicting values across sources/time periods?
- **Why it matters:** Financial inconsistency is common; wrong merge logic breaks trust.
- **Options:**
  1. Latest authoritative source wins
  2. Priority hierarchy wins (regulatory > exchange > IR > others)
  3. Multi-source compare + flag unresolved conflict
- **Recommended starting point:** Hierarchy + recency + explicit conflict flag.
- **Owner:** Engineering
- **Target decision by:** Before financial claim builder freeze

---

## OQ-12: Ambiguity Handling for Company Resolution (New)

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** What to do when input maps to multiple similar entities?
- **Why it matters:** Wrong-company research is a critical failure.
- **Recommended starting point:**
  - Block full run on unresolved ambiguity
  - Return disambiguation candidates
  - Require explicit selection
- **Owner:** Engineering
- **Target decision by:** Before public API stabilization

---

## OQ-13: Governance/Risk Content Guardrails (New)

- **Status:** OPEN
- **Priority:** HIGH
- **Decision needed:** Rules for sensitive negative assertions (litigation/governance/controversy).
- **Why it matters:** High legal/reputational risk if unsupported or speculative.
- **Recommended starting point:**
  - Require stronger evidence threshold
  - Require explicit citation granularity
  - Use neutral phrasing when evidence incomplete
- **Owner:** Product + Engineering
- **Target decision by:** Before report language policy freeze

---

## Notes

- Convert each `OPEN` item to `DECIDED` with:
  - Decision date
  - Decision owner
  - Final policy text
  - Implementation ticket links
- If deferred, mark `DEFERRED` with reason and revisit date.