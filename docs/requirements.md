# Requirements

## 1. Project Objective

Build a deep-research equity analysis system that can research a listed company and generate a comprehensive, citation-backed Markdown investment research report.

The initial MVP will focus on Indian listed equities, while keeping the architecture extensible for future US equity support.

---

## 2. Initial Research Areas

The system should be capable of researching:

### Business

* Business model
* Products/services
* Business segments
* Markets served
* Customers
* Competition
* Competitive advantages / moat
* Growth drivers
* Business risks

### Financials

* Revenue
* Profit
* Margins
* Cash flow
* Balance sheet
* Debt
* Capex
* Financial ratios
* Historical performance
* Current financial position
* Relevant annual reports, AGMs and investor calls

### Management / Promoters

* Background
* Experience
* Track record
* Shareholding
* Promoter holding and pledging
* Other businesses
* Related-party transactions
* Management changes
* Regulatory/governance concerns
* Relevant controversies or litigation
* Credibility and execution history

---

## 3. Research Workflow

The system should follow a structured research process rather than relying on a single LLM prompt.

Initial direction:

```text
User Input
    ↓
Company Resolution
    ↓
Research Planner / Orchestrator
    ↓
Research Tasks
    ↓
Source Discovery / Retrieval
    ↓
Evidence / Extraction
    ↓
Analysis
    ↓
Investment Verdict
    ↓
Report Generation
    ↓
Citation / Validation
    ↓
Final Markdown Report
```

The architecture should allow independent research areas to be executed in parallel where appropriate.

---

## 4. Evidence and Sources

Important research claims should be traceable to their sources.

The system should prioritize authoritative sources such as:

* NSE
* BSE
* SEBI
* Company websites
* Investor-relations pages
* Annual reports
* Financial results
* Investor presentations
* AGM documents
* Investor/earnings calls
* Other relevant regulatory disclosures

The system should maintain source metadata and should never fabricate citations.

---

## 5. Research Efficiency

The system should minimize:

* Unnecessary searches
* Duplicate document retrieval
* Duplicate processing
* Duplicate LLM calls
* Excessive context
* Unnecessary research loops

The research orchestration layer should eventually support:

* Parallel research
* Caching
* Deduplication
* Research-state persistence
* Cost/token tracking
* Retry handling
* Research budget/caps

A research budget or stopping condition should allow the system to stop further retrieval/LLM work when sufficient evidence has been collected for a research task.

The exact stopping strategy is still to be finalized.

---

## 6. Investment Verdict

The final report must contain an Investment Verdict.

The exact verdict framework is not yet finalized and should remain independently replaceable.

The report should distinguish between:

* Sourced facts
* Analytical interpretation
* Model-generated conclusions

---

## 7. Final Report

The MVP should generate a Markdown report containing at least:

1. Business overview
2. Investment verdict
3. Moat
4. Financial summary
5. Relevant historical financial information
6. AGM / investor-call information
7. Promoter and management deep dive

Important claims should include appropriate citations.

---

## 8. Future Compatibility

The architecture should remain capable of supporting:

* US equities
* Additional financial data sources
* Valuation
* Peer comparison
* Price analysis
* Price prediction
* Portfolio-level analysis

These are not initial MVP requirements.

---

## 9. Engineering Priorities

The project should prioritize:

1. Correctness
2. Evidence and traceability
3. Modularity
4. Cost efficiency
5. Execution time
6. Scalability

The goal is to build a reliable equity-research engine rather than a generic AI agent.
