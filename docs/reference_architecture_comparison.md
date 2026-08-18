# Reference Architecture Comparison

## Purpose

Vinit Bhaiya suggested two projects as references:

1. LangChain Open Deep Research
2. GPT Researcher

The goal is not to copy either project, but to understand the common research patterns and decide what fits EquityScout.

---

# 1. Open Deep Research

Repository:

https://github.com/langchain-ai/open_deep_research

Open Deep Research is a configurable deep-research agent using LangGraph. It supports multiple LLM providers, search tools and MCP.

One useful idea is that it separates LLM responsibilities:

* Summarization
* Research
* Compression
* Final report generation

It also supports different search mechanisms and structured outputs/tool calling.

### What I found useful

* Explicit research workflow/state
* Search abstraction
* Configurable models
* Structured outputs
* Parallel research
* Separation of research and final report

The repository also contains earlier plan-and-execute and multi-agent implementations, which are useful for understanding different approaches.

### What we should avoid copying

We don't need the complete Open Deep Research architecture.

EquityScout has a much narrower domain, so adding every model role, MCP integration or multi-agent component would increase complexity without necessarily improving the MVP.

---

# 2. GPT Researcher

Repository:

https://github.com/assafelovic/gpt-researcher

GPT Researcher follows a simple core pattern:

```text
Query
  ↓
Planner
  ↓
Research Questions
  ↓
Execution / Crawler Agents
  ↓
Sources + Findings
  ↓
Publisher
  ↓
Report
```

The planner creates questions, execution agents gather information and track sources, and the publisher combines the findings into a report.

It also supports parallel research and research over local documents.

### What I found useful

This feels comparatively closer to our use case because our system also needs to:

* Break company research into smaller questions
* Research different areas independently
* Gather evidence
* Combine findings
* Generate a final report

For EquityScout, the research questions can become domain-specific:

```text
Business
Financials
Management / Promoters
Moat
Risks
```

---

# 3. What Both Projects Have in Common

The common pattern is:

```text
Planning
   ↓
Research
   ↓
Retrieval / Sources
   ↓
Findings
   ↓
Synthesis
   ↓
Report
```

So the main lesson is not to choose a framework simply because it is popular.

The important idea is:

> **Deep research should be a structured process, not one LLM call.**

---

# 4. Direction for EquityScout

After studying both, I feel GPT Researcher is comparatively closer to our use case.

I'm not suggesting that we copy it.

My current proposal is:

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

The **Research Orchestrator** would be the most important component because it can control:

* Which research tasks are required
* Which tasks can run in parallel
* Which sources should be searched
* Whether documents have already been processed
* When enough evidence has been collected
* How much LLM/retrieval work should be performed

---

# 5. Ideas We Should Take

### From GPT Researcher

* Planner → research questions
* Parallel research
* Source tracking
* Research over documents
* Findings → final report

### From Open Deep Research

* Model abstraction
* Search abstraction
* Structured outputs
* Explicit research state
* Configurable research workflow

---

# 6. Ideas We Should Add for Equity Research

The biggest difference is that EquityScout is domain-specific.

The orchestrator should understand research pillars such as:

```text
Business
Financials
Management / Promoters
Moat
Risks
```

We should also prioritize authoritative financial sources instead of treating every web source equally.

---

# 7. Cost and Efficiency

Cost efficiency should be designed into the orchestrator.

Potential mechanisms:

```text
Research Task
     ↓
Search
     ↓
Evidence Check
     ↓
Enough evidence?
   /       \
 Yes       No
 ↓          ↓
Stop      Continue
```

Additional mechanisms:

* Caching
* Deduplication
* Reusing retrieved documents
* Parallel execution
* Model routing
* Research budgets/caps

The goal is not to maximize the number of searches or LLM calls.

The goal is to obtain **sufficient high-quality evidence with minimum unnecessary work**.

---

# 8. Initial Architectural Principle

The current direction is:

> **Take the useful research concepts from Open Deep Research and GPT Researcher, then build a simpler, domain-specific architecture around EquityScout's requirements.**

Before implementation, the major decisions around the orchestrator, research budget, model routing, parallelism and stopping conditions should be reviewed and confirmed.

This will be the basis for breaking the project into MVP milestones and implementation tasks.
