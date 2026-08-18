# Assumptions

> These are current architectural assumptions, not confirmed requirements. Major decisions should be validated with Vinit Bhaiya.

---

## 1. Research Orchestrator

### Assumption

The Research Planner/Orchestrator will be the central component responsible for coordinating the research process.

Conceptually:

```text
Company
   ↓
Research Orchestrator
   ↓
Research Tasks
   ↓
Retrieval + Evidence
   ↓
Analysis
```

### Why

Both Open Deep Research and GPT Researcher demonstrate structured research workflows rather than a single LLM call.

For EquityScout, the orchestrator can additionally control research cost, retrieval depth and execution.

---

## 2. Parallel Research

### Assumption

Independent research pillars should be capable of running in parallel.

For example:

```text
             Research Orchestrator
              /       |        \
             ↓        ↓         ↓
         Business  Financial  Management
```

This can reduce execution time, although concurrency should be controlled to avoid unnecessary API usage and rate limits.

---

## 3. Model Routing

### Assumption

The architecture should allow different models to be used for different tasks if this provides a meaningful cost/quality advantage.

For example:

* Smaller/cheaper model → simple extraction or summarization
* Stronger model → complex analysis or final synthesis

Open Deep Research provides a useful reference here because it separates model responsibilities for summarization, research, compression and final reporting.

However, multiple models are not automatically required for the first MVP.

---

## 4. Caching and Deduplication

### Assumption

The system should avoid repeatedly downloading or processing the same document.

Example:

```text
Annual Report
      ↓
Processed once
      ↓
Reusable by:
├── Financial Research
├── Business Research
└── Management Research
```

This should reduce both cost and execution time.

---

## 5. Research Budget / Stopping Condition

### Assumption

The Research Orchestrator should eventually have a mechanism to decide when enough research has been performed.

Possible signals may include:

* Required questions answered
* Sufficient high-quality sources found
* Evidence coverage reached
* Research budget exhausted
* Additional searches producing little new information

This is currently an architectural idea and should be validated before implementation.

---

## 6. Evidence Before Analysis

### Assumption

Research findings should be stored as evidence before they are passed to the analysis/report-generation stages.

Preferred flow:

```text
Source
  ↓
Retrieved Content
  ↓
Evidence / Extraction
  ↓
Analysis
  ↓
Report
```

This is important for citation traceability and reducing unsupported claims.

---

## 7. GPT Researcher as the Closer Reference

### Assumption

GPT Researcher's planner → execution → publisher pattern is currently closer to the expected EquityScout workflow than the more configurable/general Open Deep Research architecture.

However, this does not mean GPT Researcher will be copied.

Useful concepts from both projects will be combined and adapted.

---

## 8. Modular Monolith

### Assumption

The first MVP should preferably remain a modular monolith.

The initial architecture can contain separate logical modules without immediately splitting them into independent services.

---

## 9. Architecture Direction

Current working direction:

```text
User Input
    ↓
Company Resolution
    ↓
Research Planner / Orchestrator
    ↓
Evidence / Extraction Store
    ↓
Analysis
    ↓
Investment Verdict
    ↓
Report
    ↓
Validation
    ↓
Final Markdown
```

The exact internal boundaries are still subject to design review.

---

## 10. Model and Search Abstraction

### Assumption

LLM and search providers should be accessed through abstractions rather than being tightly coupled to one provider.

This allows future changes in:

* LLM provider
* Search provider
* Retrieval mechanism

without rewriting the research engine.

---

## 11. Scope Control

The MVP should avoid implementing advanced features simply because the reference projects support them.

Examples:

* Recursive research trees
* Large multi-agent hierarchies
* Complex MCP ecosystems
* Advanced prediction
* US equity workflows
* Large frontend systems

These should only be introduced when the project requirements justify them.
