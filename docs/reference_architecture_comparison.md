# Reference Architecture Comparison

## Purpose

Vinit Bhaiya suggested two reference projects:

1. LangChain Open Deep Research  
2. GPT Researcher

The objective is **not** to copy either repository.  
The objective is to extract reusable deep-research patterns and adapt them to EquityScout’s evidence-first equity workflow.

---

## 1) LangChain Open Deep Research

Repository:  
https://github.com/langchain-ai/open_deep_research

Open Deep Research is a configurable deep-research system (LangGraph-based) with support for multiple model/tool providers and flexible orchestration patterns.

### Relevant ideas for EquityScout

- Explicit workflow/state management for multi-step research
- Model-role separation (e.g., summarization vs synthesis)
- Search/tool abstraction layers
- Structured outputs/tool-calling patterns
- Parallelizable execution paths
- Separation between evidence-gathering and report synthesis

### What to avoid for MVP

- Copying full framework complexity
- Premature multi-agent hierarchies
- Broad MCP/tool ecosystem integration without clear MVP need
- Over-configuring model roles before baseline quality is proven

**Conclusion:** Useful architectural patterns, but too general/expansive to adopt wholesale for a focused India-equity MVP.

---

## 2) GPT Researcher

Repository:  
https://github.com/assafelovic/gpt-researcher

GPT Researcher follows a simpler planning-driven pattern:

```text
Query
  ↓
Planner
  ↓
Research Questions
  ↓
Execution / Crawling
  ↓
Findings + Sources
  ↓
Publisher
  ↓
Report
```

### Relevant ideas for EquityScout

- Planner-driven decomposition into smaller research questions
- Parallel execution of independent research branches
- Source tracking during execution
- Findings-first, then report synthesis
- Straightforward end-to-end flow suitable for MVP velocity

### Fit assessment

This pattern is closer to EquityScout’s near-term needs, because we also require:

- Structured question decomposition
- Multi-pillar investigation
- Evidence accumulation
- Synthesis into an investment report

**Conclusion:** Closer conceptual baseline for MVP orchestration.

---

## 3) Common Pattern Across Both

Both projects converge to the same high-level shape:

```text
Planning
   ↓
Research Execution
   ↓
Source Retrieval
   ↓
Findings/Evidence
   ↓
Synthesis
   ↓
Report
```

### Primary takeaway

> Deep research is a **process architecture**, not a single-prompt behavior.

This principle directly aligns with EquityScout’s evidence and citation requirements.

---

## 4) EquityScout Target Direction (MVP)

```text
User Input
    ↓
Company Resolution (India)
    ↓
Research Planner / Orchestrator
    ↓
Task Execution (Business / Financials / Promoters)
    ↓
Source Discovery + Selection
    ↓
Document Retrieval
    ↓
Parse / Extract
    ↓
Evidence Store (+ citation metadata)
    ↓
Analysis (claims)
    ↓
Verdict Engine
    ↓
Report Generator
    ↓
Claim/Citation Validation
    ↓
Final Markdown Report
```

### Why the Orchestrator is central

The orchestrator should control:

- Task planning and sequencing
- Parallelism limits
- Source/provider selection policy
- Caching and document reuse
- Budget/time/call limits
- Stopping conditions based on evidence sufficiency
- Error handling and retry policy

---

## 5) What to Borrow (Pragmatically)

### From GPT Researcher

- Planner → research-question decomposition
- Parallel branch execution
- Source-aware findings collection
- Findings-first report assembly

### From Open Deep Research

- Provider/model abstraction boundaries
- Explicit research state handling
- Structured outputs and typed intermediate artifacts
- Configurable workflow controls

---

## 6) EquityScout-Specific Additions (Domain Requirements)

Because EquityScout is equity-domain specific, it needs domain-aware logic absent in generic systems:

1. **Research pillars**
   - Business
   - Financials
   - Management/Promoters
   - (Moat and risk as analysis outputs/perspectives)

2. **Authority-aware source ranking**
   - Prioritize regulatory/exchange/company disclosures over generic web content

3. **Strict evidence/claim separation**
   - Sourced fact ≠ interpretation ≠ verdict

4. **Citation traceability**
   - Citation metadata must persist from extraction stage onward

5. **Finance-aware conflict handling**
   - Explicit policy for conflicting figures across documents/time periods

---

## 7) Cost and Efficiency Strategy

The goal is not maximum search volume; it is sufficient high-quality evidence with minimal waste.

```text
Research Task
     ↓
Discovery/Retrieval
     ↓
Evidence Coverage Check
   /                 \
Sufficient          Insufficient
   ↓                    ↓
Stop branch         Continue with constraints
```

### Core efficiency mechanisms

- Deduplication (URL/content hash)
- Document reuse across pillars
- Controlled parallelism
- Model routing by task complexity
- Budget/cap enforcement
- Early stopping on diminishing evidence gain

---

## 8) Recommended MVP Architectural Principle

> Combine the strongest planning/execution patterns from both reference projects, then implement a simpler modular-monolith architecture optimized for India equity evidence workflows.

This means:

- No framework copy-paste
- No premature complexity
- Strong pipeline boundaries
- Evidence-first reliability over “agent sophistication”

---

## 9) Decisions to Confirm Before/During Implementation

The following are high-impact and should be explicitly reviewed:

1. Orchestrator policy granularity (static templates vs adaptive planning)
2. Evidence sufficiency threshold per pillar
3. Stopping/budget strategy (time, token, source-depth caps)
4. Concurrency strategy (global vs provider-scoped limits)
5. Model routing strategy (single-model MVP vs multi-model routing)
6. Conflict-resolution policy for inconsistent data points
7. Citation validation strictness for “major claims”

---

## 10) Final Position

GPT Researcher is the closer conceptual fit for MVP flow.  
Open Deep Research contributes valuable abstraction/state ideas.

EquityScout should synthesize both into a domain-specific, evidence-first architecture that prioritizes:

1. Correctness  
2. Traceability  
3. Reliability  
4. Cost efficiency  
5. Maintainable extensibility