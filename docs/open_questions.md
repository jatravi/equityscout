# Assumptions

> This document records assumptions made during early system design.
> Assumptions are not confirmed requirements.
> Any assumption that materially affects architecture should be validated with the project mentor.

---

# 1. MVP Market Assumption

### Assumption

The first production-quality MVP will focus only on Indian listed equities.

### Reason

Supporting India and the US simultaneously would increase complexity in:

- Company identification
- Exchange identification
- Regulatory sources
- Filing formats
- Data providers
- Document retrieval
- Source validation
- Research workflows

### Architectural implication

India-specific implementations should be isolated behind interfaces/adapters where practical.

### Status

Reasonable assumption based on the current project specification.

---

# 2. Report Format Assumption

### Assumption

The primary MVP output will be Markdown.

### Reason

The project specification explicitly requires a comprehensive Markdown investment research report.

### Architectural implication

Report generation should be separated from research and evidence collection so that PDF, DOCX, HTML, or UI output can be added later.

### Status

Confirmed for MVP.

---

# 3. Research Task Assumption

### Assumption

Research should be decomposed into specialized tasks instead of relying on one general research prompt.

### Reason

The project requires deep research across different dimensions such as business, financials, management, moat, and risks.

Both reference systems also use structured research workflows rather than a single unrestricted generation call.

GPT Researcher explicitly describes a planner that generates research questions followed by execution agents that gather information and a publisher that aggregates findings. :contentReference[oaicite:4]{index=4}

Open Deep Research also demonstrates a configurable research-agent workflow with distinct research, summarization, compression, and report-generation responsibilities. :contentReference[oaicite:5]{index=5}

### Architectural implication

The system should contain some form of:

    Research Planner
          ↓
    Research Tasks
          ↓
    Research Execution
          ↓
    Evidence
          ↓
    Synthesis

### Status

Strong architectural assumption. Validate implementation details with mentor.

---

# 4. Parallel Research Assumption

### Assumption

Independent research tasks should be capable of running concurrently.

For example:

    Business Research
           │
    Financial Research
           │
    Management Research

may be executed independently.

### Reason

GPT Researcher explicitly emphasizes parallelized agent work, and its architecture describes separate execution agents gathering information for generated questions. :contentReference[oaicite:6]{index=6}

Open Deep Research's legacy multi-agent implementation also describes parallel processing with multiple researchers working simultaneously. :contentReference[oaicite:7]{index=7}

### Architectural implication

Research task execution should not be tightly coupled to sequential execution.

### Status

To be validated against MVP complexity and expected runtime.

---

# 5. Primary-Source Preference Assumption

### Assumption

Primary and authoritative sources should be preferred over secondary sources whenever the required information is available from a primary source.

### Reason

The project's research-integrity requirements explicitly prioritize primary sources.

### Architectural implication

Sources should have metadata describing source type and authority.

A source-ranking mechanism may be required.

### Status

Strong requirement/assumption.

---

# 6. Evidence-First Assumption

### Assumption

The system should store evidence separately from the final report.

### Reason

Important conclusions must be traceable to supporting evidence.

### Architectural implication

The architecture should resemble:

    Source
       ↓
    Evidence
       ↓
    Claim
       ↓
    Analysis
       ↓
    Report

rather than:

    Source
       ↓
    LLM
       ↓
    Report

### Status

Strong architectural assumption.

---

# 7. Citation-First Architecture Assumption

### Assumption

Citation metadata should be preserved throughout the research pipeline rather than generated at the final report stage.

### Reason

Generating citations after analysis risks unsupported or incorrect citations.

### Architectural implication

Evidence objects should retain source metadata such as:

- URL
- Document
- Page
- Section
- Publication date
- Retrieval timestamp

### Status

Recommended architecture.

---

# 8. Modular Monolith Assumption

### Assumption

The MVP should initially be implemented as a modular monolith rather than a collection of microservices.

### Reason

The project specification explicitly advises against unnecessary microservices for the MVP.

### Architectural implication

Modules should have clean interfaces even if they initially run in one application.

### Status

Recommended.

---

# 9. LLM Abstraction Assumption

### Assumption

LLM providers should be accessed through an abstraction layer.

### Reason

The system may eventually use different providers/models for:

- Research
- Extraction
- Summarization
- Compression
- Final report generation

Open Deep Research itself separates model responsibilities and supports multiple model providers. :contentReference[oaicite:8]{index=8}

### Architectural implication

Business logic should not depend directly on one LLM provider.

### Status

Recommended.

---

# 10. Search Abstraction Assumption

### Assumption

Search should be represented as an abstraction rather than being permanently tied to one search provider.

### Reason

Open Deep Research supports multiple search tools and MCP-based integrations. :contentReference[oaicite:9]{index=9}

GPT Researcher also supports multiple retrieval mechanisms, including web search and MCP. :contentReference[oaicite:10]{index=10}

### Architectural implication

A search interface/provider layer should exist.

### Status

Recommended.

---

# 11. Document Reuse Assumption

### Assumption

Documents retrieved during one research task should be reusable by other research tasks.

### Reason

The same annual report may contain:

- Financial information
- Management information
- Business information
- Risk information

Repeatedly downloading the same document would increase latency and cost.

### Architectural implication

Document identity and content hashes should be maintained.

### Status

Recommended.

---

# 12. Research-State Assumption

### Assumption

The system should persist research state sufficiently to support:

- Retries
- Debugging
- Reproducibility
- Partial failure recovery
- Cost tracking

### Architectural implication

Research execution should maintain explicit state rather than relying entirely on transient Python variables.

### Status

Recommended.

---

# 13. Verdict Engine Assumption

### Assumption

The investment-verdict framework is not finalized.

### Reason

The current requirements explicitly state that the exact framework should not be invented as a confirmed requirement.

### Architectural implication

The verdict engine should be replaceable.

### Status

Must be confirmed with Vinit.

---

# 14. Historical Financial Depth Assumption

### Assumption

The MVP requires enough historical information to identify meaningful financial trends, but the exact number of years is not yet fixed.

### Reason

The specification explicitly avoids permanently hard-coding a historical depth.

### Architectural implication

Research planning should eventually be capable of determining the required historical depth.

### Status

Needs mentor confirmation.

---

# 15. UI Assumption

### Assumption

A sophisticated frontend is not required for the first MVP unless explicitly requested.

### Reason

The confirmed initial output is a Markdown research report.

### Architectural implication

The research engine should be usable independently from a frontend.

### Status

Needs mentor confirmation.

---

# 16. Deployment Assumption

### Assumption

Deployment requirements should be treated separately from research-engine architecture until the MVP workflow is stable.

### Reason

Premature deployment complexity may slow research-system development.

### Status

Needs confirmation based on internship expectations.

---

# 17. Financial Data Assumption

### Assumption

Financial data should preferably come from authoritative filings and company/exchange sources instead of relying entirely on third-party financial APIs.

### Reason

The project emphasizes source authenticity and citation.

### Architectural implication

Financial data providers should be replaceable and source metadata should be retained.

### Status

Recommended.

---

# 18. Research Integrity Assumption

### Assumption

An LLM-generated statement is never considered evidence by itself.

### Reason

The project explicitly requires separation between sourced facts and model-generated analysis.

### Architectural implication

Evidence and model reasoning must remain distinguishable.

### Status

Strong requirement.