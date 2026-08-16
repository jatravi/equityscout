# Requirements

## 1. Project Overview

The project is an AI-powered deep-research equity analysis system.

The system should accept a publicly listed company as input, conduct structured research using reliable sources, analyse the collected information, and generate a comprehensive Markdown investment research report with citations.

The initial MVP will focus on Indian listed equities.

The architecture should remain extensible so that US equities and additional financial-analysis capabilities can be added later without rewriting the complete research engine.

---

# 2. Project Objective

The primary objective is to build a reliable, citation-backed, cost-efficient deep-research engine for equity analysis.

Given an Indian listed company, the system should:

1. Identify the company.
2. Create an appropriate research plan.
3. Discover relevant sources.
4. Retrieve relevant documents and information.
5. Process the retrieved information.
6. Extract evidence.
7. Conduct structured research and analysis.
8. Cross-check important information where appropriate.
9. Produce an investment analysis.
10. Generate a cited Markdown research report.
11. Validate that important claims have supporting evidence.

The system should prioritize evidence and source authenticity rather than relying on unsupported LLM-generated knowledge.

---

# 3. Initial MVP Scope

## 3.1 Market

The initial MVP is limited to:

- Indian publicly listed companies.

US equity support is not part of the initial MVP.

However, the architecture should avoid unnecessary India-specific coupling so that US support can later be added through additional providers, source adapters, and workflows.

---

# 4. Input Requirements

The system should accept a company/equity as input.

Example:

    Reliance Industries

The system should resolve the input to the correct company where possible.

Potential company identifiers may include:

- Company name
- Trading symbol
- Exchange
- ISIN
- Other supported identifiers

The exact company-resolution interface is to be finalized during architecture design.

---

# 5. Research Requirements

The system should perform structured research rather than sending a single broad prompt to an LLM.

The research process should be capable of decomposing the overall research problem into specialized research tasks.

Initial research areas include:

## 5.1 Business Research

The system should investigate:

- What the company does
- Business model
- Products and services
- Business segments
- Revenue/business segments
- Markets served
- Customers
- Industry
- Competitive landscape
- Competitive advantages
- Business risks
- Growth drivers
- Moat

---

## 5.2 Financial Research

The system should investigate:

- Revenue
- Profit
- Margins
- Cash flows
- Balance sheet
- Debt
- Capital expenditure
- Growth trends
- Key financial ratios
- Segment information where relevant
- Current financial position
- Historical financial performance

The research should consider:

- Current financial information
- Previous annual reports
- Annual General Meetings (AGMs)
- Investor/earnings calls
- Investor presentations
- Relevant official financial disclosures

The system should not permanently hard-code a fixed historical period if the architecture can support dynamic research depth.

---

## 5.3 Management and Promoter Research

The system should investigate relevant information about promoters and management.

Potential areas include:

- Background
- Experience
- Track record
- Shareholding
- Promoter holding
- Share pledging
- Other businesses
- Related-party transactions
- Management changes
- Regulatory issues
- Controversies
- Litigation
- Governance concerns
- Credibility
- Historical execution

The system should focus on information relevant to investment analysis and avoid unnecessary personal information.

---

# 6. Report Requirements

The MVP should generate a comprehensive Markdown research report.

The currently confirmed report sections are:

## 6.1 Business Overview

A concise but useful explanation of:

- What the company does
- Business model
- Major products/services
- Major business segments
- Markets
- Competitive position

---

## 6.2 Investment Verdict

The report must contain an investment verdict.

However, the exact investment-verdict framework is not yet finalized.

The system should therefore keep the verdict generation mechanism replaceable.

The verdict should distinguish between:

- Sourced facts
- Analytical interpretation
- Model-generated conclusions

The system should provide reasoning and supporting evidence for conclusions.

---

## 6.3 Moat

The report should analyse the company's competitive advantages and potential economic moat.

The analysis should be evidence-based.

---

## 6.4 Financial Summary

The financial section should include relevant current and historical information.

It should incorporate information from:

- Current financial results
- Previous annual reports
- Previous AGMs
- Investor/earnings calls
- Investor presentations
- Other authoritative financial disclosures where relevant

---

## 6.5 Promoter and Management Deep Dive

The report should provide a deep dive into promoters and management.

It should include:

- Credibility
- Track record
- Relevant ownership information
- Governance-related information
- Other relevant information affecting investor confidence

---

# 7. Source Requirements

Source quality is a core requirement.

The system should prioritize authoritative and primary sources.

Potential Indian equity sources include:

- NSE
- BSE
- SEBI
- Company official websites
- Company investor-relations pages
- Annual reports
- Financial results
- Investor presentations
- AGM documents
- Earnings/investor call transcripts or recordings where legitimately available
- Shareholding disclosures
- Promoter disclosures
- Corporate announcements
- Regulatory filings

The system should support a source hierarchy rather than assuming that every fact must come from one source.

---

# 8. Citation Requirements

Citation is a core feature.

Important claims should be traceable to their supporting source.

Citations should be provided for important:

- Financial figures
- Management/promoter information
- Corporate events
- Business facts
- Regulatory information
- Material risks
- Investment conclusions where supporting evidence exists

Where possible, citations should point to the original source or document.

Source metadata should be retained.

Relevant metadata includes:

- Source URL
- Source type
- Document title
- Publication date
- Company
- Document period
- Retrieval timestamp
- Relevant page/section
- Extracted information
- Research task that used the source

The system must never fabricate citations.

If information cannot be verified, the report should explicitly indicate that it could not be verified.

---

# 9. Research Workflow Requirements

The research workflow should conceptually support:

    User Input
        ↓
    Company Identification
        ↓
    Research Planning
        ↓
    Research Task Generation
        ↓
    Source Discovery
        ↓
    Document Retrieval
        ↓
    Document Processing
        ↓
    Evidence Extraction
        ↓
    Research/Synthesis
        ↓
    Cross-checking
        ↓
    Investment Analysis
        ↓
    Report Generation
        ↓
    Citation Validation

Research tasks may include:

- Business research
- Financial research
- Management/promoter research
- Moat/competitive research
- Risk research
- Recent developments

Tasks should be capable of running independently or in parallel where appropriate.

---

# 10. Cost and Performance Requirements

The system should minimize:

- Unnecessary web searches
- Duplicate document retrieval
- Duplicate LLM calls
- Excessive context
- Repeated summarization
- Unnecessary agent loops
- Expensive model usage

Deterministic processing should be preferred where possible.

LLMs should primarily be used where reasoning, synthesis, classification, extraction, or interpretation is actually required.

The architecture should support:

- Caching
- Deduplication
- Source reuse
- Document reuse
- Research-state persistence
- Token/cost tracking
- Retry policies
- Model selection by task

---

# 11. Reliability Requirements

The system should not confidently produce unsupported information.

It should handle failures including:

- Missing documents
- Broken URLs
- Rate limits
- Search failures
- Parsing failures
- LLM failures
- Conflicting information
- Outdated information

The system should provide appropriate failure states instead of silently inventing information.

---

# 12. Reproducibility Requirements

A research run should ideally be reproducible.

The system should retain enough metadata to determine:

- Which sources were used
- When they were retrieved
- Which research tasks used them
- What evidence was extracted
- Which analysis was generated
- Which report was produced

---

# 13. Future Requirements

The architecture should remain capable of supporting future capabilities.

Potential future requirements include:

## 13.1 US Equities

- US company identifiers
- US exchanges
- SEC filings
- US financial sources
- US investor-relations pages
- US-specific document formats

---

## 13.2 Valuation

Potential future capabilities:

- P/E
- P/B
- EV/EBITDA
- DCF
- Comparable-company analysis
- Other valuation methodologies

---

## 13.3 Price Analysis

Potential future capabilities:

- Historical price analysis
- Technical analysis
- Quantitative analysis
- Market trends

---

## 13.4 Price Prediction

Potential future capabilities:

- Price prediction
- Forecasting
- Predictive models

These are not MVP requirements.

---

# 14. Non-Functional Priorities

The project should prioritize:

1. Correctness
2. Evidence
3. Modularity
4. Cost efficiency
5. Latency
6. Scalability

The system should not optimize for architectural complexity.

The objective is to build a reliable research engine rather than a generic AI agent.