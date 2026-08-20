# Assumptions and Confirmed Decisions (MVP)

This document keeps track of the main decisions and assumptions for the EquityScout MVP.

The idea is simple:

- **✅ Confirmed** → already agreed direction 

- **🟡 Assumption** → my current approach, which can still change after testing or discussion 

The goal is to avoid mixing confirmed requirements with things that I'm currently proposing.

---

## 1. What are we building?

-  ✅ EquityScout is mainly an **evidence-first equity research system**, not a general stock chatbot. 

-  ✅ The final output should be a **Markdown investment research report with citations**. 

-  ✅ Important claims in the report should be traceable back to the actual source. 

-  ✅ If we don't have enough reliable information, the system should say that instead of making up or overconfidently generating an answer. 

---

## 2. MVP Scope

For the first version, we are keeping the scope focused.

-  ✅ MVP will focus only on **Indian listed companies**. 

-  ✅ The three main research areas are: 

  1.  Business 

  2.  Financials 

  3.  Promoters / Management 

The report should currently include:

1.  Brief about the business 

2.  Investment verdict 

3.  Moat 

4.  Financial summary, including current and previous reports/AGM/investor communication wherever relevant 

5.  Deep dive into promoters and their credibility/relevant information 

-  ✅ Things like valuation, peer comparison, technical analysis, price prediction and US stocks are **not part of the MVP right now**. 

---

## 3. Overall Architecture

-  ✅ For the MVP, we'll keep it as a **modular monolith**. 

That means one codebase, but the different parts of the system should still have clear responsibilities and boundaries.

We should also persist the research state so that we can debug failures, retry tasks and understand what happened during a research run.

-  🟡 Microservices can be considered later if the project actually reaches a point where they are needed. 

For now, there is no reason to add that complexity.

---

## 4. Research Orchestrator

One of the main parts of the system will be the **Research Orchestrator**

It will coordinate the overall research flow.

```
Company Input
   ↓
Company Resolution
   ↓
Research Orchestrator
   ↓
Task Planning + Execution
   ↓
Source Discovery / Selection
   ↓
Retrieval + Parsing + Extraction
   ↓
Evidence Store
   ↓
Analysis + Verdict
   ↓
Report + Validation
```
-  ✅ We are not going with a simple `one prompt → final report` approach. 

-  🟡 The exact planning approach can evolve. 

For example, initially we may use a fixed structure for the three main pillars. Later, if needed, the planner can become more adaptive based on the company or research requirements.

---

## 5. Research Tasks

-  ✅ Research will be divided into structured tasks around: 

  -  Business 

  -  Financials 

  -  Promoters / Management 

Instead of creating completely separate systems for each pillar, the idea is to have a **common execution pipeline** and provide different goals or instructions depending on the task.

For example:

```
Business Task
    ↓
Financial Task
    ↓
Promoter Task
    ↓
Common Research / Retrieval Pipeline
```
-  🟡 At least for the MVP, I don't think we need separate autonomous agents for every pillar. 

We can introduce that later only if testing shows that it actually improves quality.

---

## 6. Parallel Processing

-  ✅ Independent tasks can run in parallel. 

For example, Business, Financial and Promoter research don't necessarily need to wait for each other.

At the same time, we need controlled concurrency because of:

-  API limits 

-  Rate limits 

-  Cost 

-  Retries 

-  System resources 

-  🟡 The exact concurrency policy can be finalized after some benchmark runs. 

---

## 7. Evidence, Claims and Verdict

One important separation in the system will be:

```
Evidence / Sourced Fact
    ↓
Analysis / Claim
    ↓
Investment Verdict
```

These should not be treated as the same thing.

-  ✅ A fact extracted from an annual report or filing is evidence. 

-  ✅ Analysis based on that evidence is a claim or interpretation. 

-  ✅ The final investment conclusion is the verdict. 

Also:

-  ✅ LLM-generated text by itself should not become evidence. 

-  ✅ Citation information should be maintained from the beginning instead of trying to add citations only after the report is generated. 

---

## 8. Source Priority

-  ✅ We should prioritize authoritative sources first. 

The current working order is:

```
Regulatory / Official Filing
    ↓
Stock Exchange Filing
    ↓
Company Investor Relations
    ↓
Official Company Communication
    ↓
High-quality Secondary Source
    ↓
General Web
```
-  🟡 This is the starting point. The exact ranking and scoring can change after we test it with real companies and documents. 

---

## 9. How we use LLMs

-  ✅ We should not use an LLM for things that can be handled easily and reliably with normal code. 

Examples:
-  URL deduplication 
-  Downloading documents 
-  Metadata parsing 
-  Hashing 
-  Basic filtering 
The general approach should be:

1.  Use deterministic logic first. 
2.  Use a cheaper/smaller model when it is sufficient. 
3.  Use a stronger model only when more complex reasoning or synthesis is actually needed. 

-  🟡 Multiple-model routing is something we can add later if benchmarks show a real cost or quality benefit. 

For the first MVP, using a single model is also completely fine.

---

## 10. Caching and Reuse

-  ✅ If the same document is useful for multiple research tasks, we should reuse it. 
-  ✅ We should avoid downloading or parsing the same source repeatedly. 
-  ✅ Canonical URLs and content hashes can help with this. 
-  ✅ Intermediate results and research state should be stored for debugging and reliability. 

For example, an annual report might be useful for both Financial and Management research, so processing it again would be unnecessary.

---

## 11. Handling Failures

The system should handle situations such as:

-  Broken links 
-  Download failures 
-  Parsing failures 
-  Rate limits 
-  Outdated documents 
-  Conflicting information 
-  LLM failures 
-  ✅ The system should record what it tried, what failed, what was skipped and the reason. 

We shouldn't silently fail and still produce a confident-looking report.

-  🟡 More advanced stopping logic, such as evidence saturation or diminishing returns, can be added gradually once the basic pipeline is stable. 

---

## 12. Investment Verdict

-  ✅ The Investment Verdict is required in the final report. 

-  ✅ The exact scoring or decision framework is still not finalized. 

-  ✅ Because of that, we should avoid tightly coupling the whole system to one verdict formula. 

The boundary can look like:

```
Evidence
   ↓
Analysis
   ↓
Verdict Engine
   ↓
Current Verdict Strategy
```

-  🟡 My current preference is to start with a narrative or criteria-based verdict instead of immediately creating a rigid numerical scoring system. 

This can be changed later once we know exactly what kind of verdict is expected.

---

## 13. Using Open Deep Research and GPT Researcher

-  ✅ Both projects are references for understanding good research patterns. 

-  ✅ We are not trying to copy their architecture directly. 

Any idea we take from them should answer:

-  What problem does this solve for EquityScout? 

-  Is the added complexity worth it? 

-  Do we actually need it in the MVP? 

GPT Researcher is currently a closer reference for the general research flow, while Open Deep Research provides useful ideas around configurable models, search and workflow structure.

---



## 14. Future Scope



-  ✅ The architecture should support future expansion without making the MVP unnecessarily complicated. 

-  ✅ India is the focus now, but we should avoid hardcoding India-specific logic everywhere. 



Possible future additions include:



-  US equities 

-  Valuation 

-  Peer comparison 

-  Market/technical analysis 

-  Prediction 



These are **not part of the current MVP** unless the scope changes.



---



## 15. Provider Abstractions

-  ✅ We should avoid tightly coupling the project to one provider. 

The main areas where abstractions can help are:

-  LLMs 
-  Search/retrieval
-  Parsing 
-  Storage 

This will make it easier to replace a provider later without rewriting the whole pipeline.

---

## 16. Things Still to be Finalized

These are some areas where we still need to validate the exact approach:

1.  🟡 What should count as a "major claim" that definitely needs a citation? 
2.  🟡 How should we handle conflicting numbers or information from different sources? 
3.  🟡 How much historical financial data should we normally analyse? 
4.  🟡 What should stop a research task — budget, time, coverage, sufficient evidence, or a combination? 
5.  🟡 What should the Investment Verdict language and confidence level look like? 
6.  🟡 What exact source ranking and freshness policy should we use?

---

## 17. Current MVP Flow

This is the current working flow:

```

User Input
    ↓
Company Resolution
    ↓
Research Run
    ↓
Planner / Orchestrator
    ↓
Business / Financials / Promoters Research Tasks
    ↓
Source Discovery + Selection
    ↓
Retrieve Documents
    ↓
Parse + Extract
    ↓
Evidence Store + Citation Metadata
    ↓
Analysis / Claims
    ↓
Verdict Engine
    ↓
Report Generator
    ↓
Claim + Citation Validation
    ↓
Final Markdown Report
```
---



### My current understanding



The main idea behind EquityScout is to keep the system **structured and evidence-driven**.



Instead of asking one model to research a company and generate everything in a single response, we break the process into smaller steps:



> **Plan → Research → Find sources → Extract evidence → Analyse → Generate verdict → Validate → Report**



The exact implementation will evolve as we start building and testing the MVP, but this document captures the current direction and the decisions we don't want to lose track of.