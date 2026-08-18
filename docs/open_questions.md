# Open Questions

> These questions should be discussed with Vinit Bhaiya before they materially affect the architecture.

---

## 1. Research Stopping Condition

How should the Research Orchestrator decide that enough research has been completed for a particular pillar?

Possible approaches:

* Fixed number of sources
* Required questions answered
* Evidence coverage
* Research budget
* Combination of quality + coverage + budget

**Priority: HIGH**

---

## 2. Research Budget

Should we define a maximum budget per company/research run?

Possible limits:

* Maximum LLM calls
* Maximum search calls
* Maximum documents
* Maximum tokens
* Maximum API cost
* Maximum execution time

**Priority: HIGH**

---

## 3. Model Routing

Do we want multiple LLMs/models in the MVP, or should we initially use one model and introduce routing after the basic pipeline works?

**Priority: MEDIUM**

---

## 4. Parallelism

Which research pillars should run in parallel?

Possible initial approach:

```text
Business
Financials
Management/Promoters
```

with other research areas added dynamically when required.

**Priority: MEDIUM**

---

## 5. Investment Verdict

What exact framework should the Investment Verdict follow?

**Priority: HIGH**

---

## 6. Historical Financial Depth

How much historical financial information should normally be researched?

For example:

* 3 years
* 5 years
* Dynamic based on company/research question

**Priority: HIGH**

---

## 7. Citation Granularity

Should important citations point to:

* Source URL
* Document + date
* Document + page/section
* Exact evidence/claim

**Priority: HIGH**

---

## 8. Evaluation

How should the MVP be evaluated?

Potential metrics:

* Citation correctness
* Research completeness
* Financial accuracy
* Source quality
* Unsupported claims
* Runtime
* Cost
* Human evaluation

**Priority: HIGH**

---

## 9. Search Provider

Which search provider should be used initially?

The architecture can remain provider-independent, but the first implementation needs a concrete provider.

**Priority: MEDIUM**

---

## 10. MVP Completion

What exact end-to-end flow should V1 demonstrate?

Current proposed minimum:

```text
Company Input
    ↓
Company Resolution
    ↓
Research Planning
    ↓
Research / Retrieval
    ↓
Evidence
    ↓
Analysis
    ↓
Verdict
    ↓
Citation Validation
    ↓
Markdown Report
```

**Priority: HIGH**
