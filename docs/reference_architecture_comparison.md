# Reference Architecture Comparison

## 1. Purpose

This document studies two open-source deep-research systems provided as architectural references:

1. LangChain Open Deep Research
2. GPT Researcher

The purpose is not to copy either project.

The objective is to understand:

- How deep-research systems are structured
- How research is planned
- How research tasks are executed
- How sources are retrieved
- How information is aggregated
- How citations are handled
- How research state is maintained
- How parallelism is achieved
- How reports are generated
- Which architectural ideas are appropriate for our equity-research system

---

# 2. Reference Project 1 — LangChain Open Deep Research

Repository:

https://github.com/langchain-ai/open_deep_research

Open Deep Research is a configurable open-source deep-research agent designed to work across multiple model providers, search tools and MCP servers.

The repository currently uses LangGraph-based orchestration.

---

## 2.1 High-Level Architecture

The current system can conceptually be understood as:

    User Query
        ↓
    Research Agent
        ↓
    Search / Tools
        ↓
    Research Findings
        ↓
    Compression
        ↓
    Final Report

The project separates different LLM responsibilities.

The current configuration includes separate model roles for:

- Search-result summarization
- Research
- Compression
- Final report generation

This is important because it avoids assuming that one model must perform every task.

---

## 2.2 Important Architectural Ideas

### A. Configurable LLM Layer

Different model roles can be configured independently.

This suggests that our system should not hard-code one LLM for all tasks.

Potential roles in our project could eventually include:

- Query/task planning
- Evidence extraction
- Financial analysis
- Synthesis
- Report generation

However, the MVP should avoid creating unnecessary model roles unless they provide measurable value.

---

### B. Search Abstraction

Open Deep Research supports multiple search mechanisms.

The current project documentation mentions:

- Search APIs
- MCP
- Native web search integrations

This suggests that our research engine should define a search abstraction.

Conceptually:

    Research Engine
          ↓
    Search Interface
       /        \
    Provider A  Provider B

This prevents the research engine from being tightly coupled to one search provider.

---

### C. Structured Outputs and Tool Calling

The selected models need to support structured outputs and tool calling.

This is important for our research planner because research tasks should ideally be represented as structured objects rather than free-form text.

For example:

    ResearchTask
    ├── task_id
    ├── task_type
    ├── question
    ├── priority
    ├── required_sources
    └── status

---

### D. LangGraph Orchestration

Open Deep Research uses LangGraph for workflow orchestration.

This demonstrates the usefulness of explicit state and graph-based workflow execution for deep research.

Potentially useful concepts:

- State
- Nodes
- Edges
- Conditional transitions
- Parallel execution
- Retry/error handling

However, we should not automatically use LangGraph everywhere.

The project should first determine whether the research workflow genuinely requires graph-based orchestration.

---

## 2.3 Legacy Implementations

The repository also contains earlier implementations.

### Workflow Implementation

The legacy workflow approach provides:

- Plan-and-execute
- Human-in-the-loop planning
- Sequential section generation
- Reflection
- Interactive approval

### Multi-Agent Implementation

The legacy multi-agent approach provides:

- Supervisor/researcher architecture
- Multiple researchers
- Parallel processing
- MCP integration

These are useful for understanding alternative designs.

The current repository notes that these legacy implementations are less performant than the current implementation but are useful for understanding alternative approaches.

---

## 2.4 What We Should Learn

Potentially useful ideas:

- Explicit research state
- Configurable model providers
- Search abstraction
- Tool calling
- Structured outputs
- Graph-based orchestration
- Parallel research
- Separate synthesis/report generation
- Evaluation framework
- Observability

---

## 2.5 What We Should NOT Copy Blindly

We should not automatically copy:

- Complete LangGraph architecture
- Every model role
- Every configuration option
- Every MCP integration
- Complex evaluation infrastructure
- Deployment architecture

Reason:

Our problem is narrower.

We are building an equity research engine rather than a general-purpose research agent.

---

# 3. Reference Project 2 — GPT Researcher

Repository:

https://github.com/assafelovic/gpt-researcher

GPT Researcher is a deep-research system designed for web and local research.

Its architecture explicitly describes three major conceptual roles:

    Planner
       ↓
    Execution Agents
       ↓
    Publisher

---

## 3.1 Planner

The planner receives the research query and generates research questions.

Conceptually:

    User Query
        ↓
    Planner
        ↓
    Research Questions

Example:

    "Research Reliance Industries"

could become:

    Q1: What is the company's business model?
    Q2: What are its major business segments?
    Q3: What has happened to revenue and margins?
    Q4: What is the company's debt position?
    Q5: Who are the major promoters?
    Q6: What are the key competitive advantages?
    Q7: What are the major risks?

This approach maps strongly to our project.

---

## 3.2 Execution Agents

Each generated research question is then investigated.

Conceptually:

    Q1 ──→ Research Agent ──→ Sources ──→ Findings
    Q2 ──→ Research Agent ──→ Sources ──→ Findings
    Q3 ──→ Research Agent ──→ Sources ──→ Findings

Independent questions can be executed in parallel.

This is particularly relevant for our:

- Business research
- Financial research
- Management research
- Moat research
- Risk research

---

## 3.3 Source Tracking

GPT Researcher explicitly describes summarizing and source-tracking each resource.

This is highly relevant to our evidence architecture.

We should retain source information together with extracted evidence.

Conceptually:

    Source
      ↓
    Retrieved Content
      ↓
    Summary / Evidence
      ↓
    Research Task
      ↓
    Final Report

---

## 3.4 Aggregation / Publisher

The publisher aggregates research findings into a final report.

Conceptually:

    Findings
       ↓
    Filter
       ↓
    Aggregate
       ↓
    Report

Our system should adapt this idea into an evidence-aware synthesis layer.

---

## 3.5 Parallelism

GPT Researcher emphasizes parallelized research.

Benefits:

- Lower execution time
- Independent tasks can run simultaneously
- Better utilization of resources

Potential downside:

- More simultaneous API calls
- Higher peak cost
- Greater rate-limit risk
- More complex state management

Therefore parallelism should be controlled rather than unlimited.

---

## 3.6 Local Documents

GPT Researcher supports research over local documents.

This is relevant because our equity system will need to process documents such as:

- Annual reports
- Investor presentations
- AGM documents
- Financial reports

This reinforces the need for a document-retrieval and document-processing layer rather than relying only on web snippets.

---

## 3.7 MCP

GPT Researcher supports MCP integration for connecting research to specialized sources such as:

- GitHub
- Databases
- Custom APIs

This demonstrates that retrieval should eventually be extensible.

However, MCP should not automatically be a mandatory MVP dependency.

---

## 3.8 Observability

GPT Researcher supports LangSmith tracing for research workflows.

This is important for our system because deep-research workflows can become difficult to debug.

Potential future telemetry:

- Research task
- Search calls
- Retrieved sources
- LLM calls
- Token usage
- Duration
- Errors
- Retries
- Final report

---

# 4. Comparison

| Area | Open Deep Research | GPT Researcher | Relevance to Our Project |
|---|---|---|---|
| Planning | Research agent / graph workflow | Explicit planner | HIGH |
| Task decomposition | Yes | Yes | HIGH |
| Parallelism | Supported | Strong emphasis | HIGH |
| Search abstraction | Yes | Multiple retrieval methods | HIGH |
| MCP | Yes | Yes | MEDIUM |
| Source tracking | Research workflow | Explicit source tracking | VERY HIGH |
| Local documents | Supported through research/tooling | Explicitly supported | VERY HIGH |
| LLM abstraction | Strong | Multiple providers | HIGH |
| Structured outputs | Important | Used in workflow | HIGH |
| State management | LangGraph | Research context/state | HIGH |
| Report generation | Dedicated final report model | Publisher/report writer | HIGH |
| Observability | LangSmith/LangGraph ecosystem | LangSmith support | HIGH |
| Evaluation | Deep Research Bench | Evaluation infrastructure | HIGH |
| General-purpose scope | High | High | We should narrow |
| Complexity | Potentially high | High | Keep MVP simpler |

---

# 5. Common Architecture Pattern

Both systems suggest a common deep-research pattern:

    User Query
         ↓
    Research Planning
         ↓
    Task Decomposition
         ↓
    Search / Retrieval
         ↓
    Source Processing
         ↓
    Evidence / Findings
         ↓
    Aggregation
         ↓
    Synthesis
         ↓
    Report

This pattern appears more important than any specific framework.

Therefore our system should implement the underlying research concepts rather than directly copying either repository.

---

# 6. Proposed Architecture for Our Project

Our project should specialize the general deep-research architecture for equity research.

    Company Input
          ↓
    Company Resolver
          ↓
    Research Planner
          ↓
    ┌─────┼───────────────┐
    ↓     ↓               ↓
 Business Financial   Management
 Research Research    Research
    ↓     ↓               ↓
    └─────┼───────────────┘
          ↓
    Source Discovery
          ↓
    Source Ranking
          ↓
    Document Retrieval
          ↓
    Document Processing
          ↓
    Evidence Extraction
          ↓
    Evidence Store
          ↓
    Cross Verification
          ↓
    Investment Analysis
          ↓
    Verdict Engine
          ↓
    Report Generator
          ↓
    Citation Validator
          ↓
    Markdown Report

---

# 7. Key Differences from the Reference Systems

Our system should not be a generic research agent.

It should be domain-specific.

The research planner should understand equity research concepts such as:

- Annual reports
- AGMs
- Investor calls
- Promoter holdings
- Share pledging
- Financial statements
- Business segments
- Moat
- Governance
- Corporate actions
- Regulatory disclosures

The source hierarchy should also be domain-specific.

For example:

    Regulatory / Exchange Filing
              ↓
    Company Investor Relations
              ↓
    Official Company Communication
              ↓
    High-quality Secondary Source
              ↓
    General Web Source

This is more appropriate for investment research than a generic web-research hierarchy.

---

# 8. Architecture Ideas to Adopt

## Adopt

### 1. Explicit research planning

Use a planner to convert the company research objective into structured research tasks.

### 2. Parallel independent research

Allow independent research tasks to execute concurrently where appropriate.

### 3. Source tracking

Every extracted finding should retain source information.

### 4. Research state

Maintain explicit state throughout a research run.

### 5. Search abstraction

Avoid hard-coding the research engine to one search provider.

### 6. LLM abstraction

Avoid hard-coding the entire system to one model/provider.

### 7. Separate synthesis from retrieval

Research agents should gather evidence; report generation should synthesize evidence.

### 8. Observability

Record enough information to understand what happened during a research run.

### 9. Evaluation

Create repeatable evaluation cases instead of relying only on subjective inspection.

---

# 9. Architecture Ideas to Adapt

## Adapt

### Planner

Generic research questions should become equity-specific research tasks.

### Source ranking

Generic source aggregation should become a financial-research source hierarchy.

### Document processing

Document processing should prioritize:

- Annual reports
- Financial results
- AGM documents
- Investor presentations
- Exchange filings

### Evidence

Evidence should preserve page/section-level information where possible.

### Report generation

The report schema should be fixed enough to satisfy the MVP requirements while remaining extensible.

---

# 10. Architecture Ideas to Avoid Initially

Do not initially implement:

- Large multi-agent hierarchies
- Multiple independent LLM providers
- Complex MCP ecosystems
- AI-generated images
- Large frontend systems
- Recursive research trees
- Advanced prediction models
- US equity workflows
- Complex microservices

These can be added later if requirements justify them.

---

# 11. Recommended MVP Architecture

The first implementation should preferably be a modular monolith.

Suggested modules:

    app/
    ├── company/
    │   └── resolver
    │
    ├── research/
    │   ├── planner
    │   ├── tasks
    │   └── executor
    │
    ├── search/
    │   └── providers
    │
    ├── sources/
    │   ├── registry
    │   └── ranking
    │
    ├── documents/
    │   ├── downloader
    │   ├── parser
    │   └── extractor
    │
    ├── evidence/
    │   └── store
    │
    ├── analysis/
    │   ├── business
    │   ├── financial
    │   ├── management
    │   ├── moat
    │   └── verdict
    │
    ├── report/
    │   ├── generator
    │   └── citation_validator
    │
    └── infrastructure/
        ├── llm
        ├── storage
        ├── cache
        └── telemetry

---

# 12. Main Architectural Lesson

The most important lesson from both reference systems is not:

"Use LangGraph."

or:

"Use GPT Researcher."

The important lesson is:

    Do not treat deep research as one LLM call.

Instead:

    Plan
      ↓
    Decompose
      ↓
    Retrieve
      ↓
    Track Sources
      ↓
    Extract Evidence
      ↓
    Synthesize
      ↓
    Validate
      ↓
    Report

Our project should implement this principle specifically for reliable equity research.