#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import requests

DEFAULT_COMPANIES = [
    "Reliance Industries", "TCS", "HDFC Bank", "Infosys", "ICICI Bank",
    "Larsen & Toubro", "Sun Pharma", "Bajaj Finance", "Tata Motors",
    "Adani Ports", "Pidilite Industries", "Avenue Supermarts",
]

STEPS = [
    ("discover", "POST", "/research-runs/{run_id}/discover-sources"),
    ("ingest", "POST", "/research-runs/{run_id}/ingest-docs"),
    ("extract", "POST", "/research-runs/{run_id}/extract-evidence"),
    ("claims", "POST", "/research-runs/{run_id}/build-claims"),
    ("report", "POST", "/research-runs/{run_id}/generate-report?include_appendix=true"),
]

@dataclass
class StageResult:
    stage: str
    status_code: int
    ok: bool
    elapsed_ms: int
    error: str | None = None

@dataclass
class CompanyBenchmarkResult:
    company: str
    run_id: str | None
    started_at: str
    finished_at: str | None
    ok: bool
    failure_stage: str | None
    stages: list[StageResult]
    report_summary: dict[str, Any] | None
    diagnostics: dict[str, Any] | None
    raw: dict[str, Any]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def request_json(session: requests.Session, method: str, url: str, timeout: int) -> tuple[int, dict[str, Any] | None, str | None]:
    try:
        resp = session.request(method=method, url=url, timeout=timeout)
        status = resp.status_code
        text = resp.text
        try:
            payload = resp.json()
        except Exception:
            payload = None
        if 200 <= status < 300:
            return status, payload, None
        msg = payload.get("detail") if isinstance(payload, dict) else text[:500]
        return status, payload, f"HTTP {status}: {msg}"
    except requests.Timeout:
        return 0, None, f"Timeout after {timeout}s"
    except Exception as e:
        return 0, None, str(e)

def request_json_with_body(session: requests.Session, method: str, url: str, json_body: dict[str, Any], timeout: int) -> tuple[int, dict[str, Any] | None, str | None]:
    try:
        resp = session.request(method=method, url=url, json=json_body, timeout=timeout)
        status = resp.status_code
        text = resp.text
        try:
            payload = resp.json()
        except Exception:
            payload = None
        if 200 <= status < 300:
            return status, payload, None
        msg = payload.get("detail") if isinstance(payload, dict) else text[:500]
        return status, payload, f"HTTP {status}: {msg}"
    except requests.Timeout:
        return 0, None, f"Timeout after {timeout}s"
    except Exception as e:
        return 0, None, str(e)

def load_companies(companies_file: str | None, max_companies: int | None) -> list[str]:
    if companies_file:
        data = json.loads(Path(companies_file).read_text(encoding="utf-8"))
        if isinstance(data, dict) and "companies" in data:
            companies = list(data["companies"])
        elif isinstance(data, list):
            companies = list(data)
        else:
            raise ValueError("companies file must be list[str] or {'companies': [...]}")
    else:
        companies = DEFAULT_COMPANIES

    companies = [c.strip() for c in companies if str(c).strip()]
    if max_companies:
        companies = companies[:max_companies]
    return companies

def run_one_company(session: requests.Session, base_url: str, company: str, stage_timeout: int) -> CompanyBenchmarkResult:
    started_at = now_iso()
    stages: list[StageResult] = []
    raw: dict[str, Any] = {"create_run": None, "steps": {}, "report_get": None, "diagnostics": None}

    create_url = f"{base_url}/research-runs"
    t0 = time.time()
    sc, payload, err = request_json_with_body(session, "POST", create_url, {"company": company}, timeout=stage_timeout)
    stages.append(StageResult("create_run", sc, err is None, int((time.time() - t0) * 1000), err))
    raw["create_run"] = payload if payload is not None else {"error": err}

    if err is not None or not payload or "runId" not in payload:
        return CompanyBenchmarkResult(company, None, started_at, now_iso(), False, "create_run", stages, None, None, raw)

    run_id = payload["runId"]
    failure_stage = None

    for stage_name, method, path in STEPS:
        url = f"{base_url}{path.format(run_id=run_id)}"
        print(f"    -> {stage_name} ...", flush=True)
        t1 = time.time()
        sc2, p2, err2 = request_json(session, method, url, timeout=stage_timeout)
        stages.append(StageResult(stage_name, sc2, err2 is None, int((time.time() - t1) * 1000), err2))
        raw["steps"][stage_name] = p2 if p2 is not None else {"error": err2}
        if err2 is not None:
            failure_stage = stage_name
            break

    report_summary = None
    diagnostics = None

    if failure_stage is None:
        sc3, report_payload, err3 = request_json(session, "GET", f"{base_url}/research-runs/{run_id}/report", timeout=stage_timeout)
        stages.append(StageResult("get_report", sc3, err3 is None, 0, err3))
        raw["report_get"] = report_payload if report_payload is not None else {"error": err3}
        if isinstance(report_payload, dict):
            report_summary = {
                "version": report_payload.get("version"),
                "verdictLabel": report_payload.get("verdictLabel"),
                "citationCount": report_payload.get("citationCount", 0),
                "reportMarkdownLength": len(report_payload.get("reportMarkdown", "") or ""),
            }

        sc4, diag_payload, err4 = request_json(session, "GET", f"{base_url}/research-runs/{run_id}/diagnostics", timeout=stage_timeout)
        stages.append(StageResult("get_diagnostics", sc4, err4 is None, 0, err4))
        raw["diagnostics"] = diag_payload if diag_payload is not None else {"error": err4}
        if isinstance(diag_payload, dict):
            diagnostics = diag_payload

    return CompanyBenchmarkResult(
        company=company,
        run_id=run_id,
        started_at=started_at,
        finished_at=now_iso(),
        ok=(failure_stage is None),
        failure_stage=failure_stage,
        stages=stages,
        report_summary=report_summary,
        diagnostics=diagnostics,
        raw=raw,
    )

def summarize(results: list[CompanyBenchmarkResult]) -> dict[str, Any]:
    total = len(results)
    ok_runs = [r for r in results if r.ok]
    fail_runs = [r for r in results if not r.ok]

    runtimes, citation_counts, unsupported_rates = [], [], []
    source_success_rates, parser_failure_rates, estimated_costs = [], [], []

    for r in ok_runs:
        runtimes.append(sum(s.elapsed_ms for s in r.stages))
        if r.report_summary:
            citation_counts.append(int(r.report_summary.get("citationCount", 0)))
        d = r.diagnostics or {}
        source_success_rates.append(float(d.get("sourceSuccessRate", 0.0)))
        parser_failure_rates.append(float(d.get("parserFailureRate", 0.0)))
        estimated_costs.append(float(d.get("estimatedCost", 0.0)))
        claims = int(d.get("claimsCount", 0))
        v_err = int(d.get("validationErrorCount", 0))
        unsupported_rates.append((v_err / claims) if claims > 0 else 0.0)

    buckets: dict[str, int] = {}
    for r in fail_runs:
        k = r.failure_stage or "unknown"
        buckets[k] = buckets.get(k, 0) + 1

    def stats(vals: list[float | int]) -> dict[str, Any]:
        if not vals:
            return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
        return {
            "count": len(vals),
            "mean": round(float(mean(vals)), 4),
            "median": round(float(median(vals)), 4),
            "min": round(float(min(vals)), 4),
            "max": round(float(max(vals)), 4),
        }

    return {
        "totalCompanies": total,
        "successfulRuns": len(ok_runs),
        "failedRuns": len(fail_runs),
        "successRate": round((len(ok_runs) / total), 4) if total else 0.0,
        "metrics": {
            "runtimeMs": stats(runtimes),
            "citationCount": stats(citation_counts),
            "unsupportedClaimRate": stats(unsupported_rates),
            "sourceSuccessRate": stats(source_success_rates),
            "parserFailureRate": stats(parser_failure_rates),
            "estimatedCost": stats(estimated_costs),
        },
        "failureBuckets": buckets,
    }

def write_json_snapshot(path: Path, results: list[CompanyBenchmarkResult]) -> None:
    payload = {
        "generatedAt": now_iso(),
        "summary": summarize(results),
        "results": [{**asdict(r), "stages": [asdict(s) for s in r.stages]} for r in results],
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

def write_outputs(out_dir: Path, results: list[CompanyBenchmarkResult], run_stamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    final_json = out_dir / f"week8_benchmark_{run_stamp}.json"
    final_md = out_dir / f"week8_benchmark_{run_stamp}.md"

    payload = json.loads((out_dir / f"week8_benchmark_{run_stamp}.partial.json").read_text(encoding="utf-8"))
    final_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    s = payload["summary"]
    lines = [
        "# Week 8 Benchmark Summary",
        f"- Generated at: `{payload['generatedAt']}`",
        f"- Total companies: **{s['totalCompanies']}**",
        f"- Successful runs: **{s['successfulRuns']}**",
        f"- Failed runs: **{s['failedRuns']}**",
        f"- Success rate: **{s['successRate']:.2%}**",
        "",
        "## Failure buckets",
    ]
    if s["failureBuckets"]:
        lines.extend([f"- {k}: {v}" for k, v in s["failureBuckets"].items()])
    else:
        lines.append("- none")

    final_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote:\n- {final_json}\n- {final_md}")

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default=os.getenv("EQUITYSCOUT_BASE_URL", "http://127.0.0.1:8000"))
    p.add_argument("--companies-file", default=None)
    p.add_argument("--max-companies", type=int, default=None)
    p.add_argument("--out-dir", default="artifacts/week8")
    p.add_argument("--stage-timeout", type=int, default=120, help="Timeout in seconds per API call")
    args = p.parse_args()

    companies = load_companies(args.companies_file, args.max_companies)
    base_url = args.base_url.rstrip("/")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    partial_json = out_dir / f"week8_benchmark_{run_stamp}.partial.json"

    print(f"Running benchmark for {len(companies)} companies against {base_url}")
    print(f"Per-stage timeout: {args.stage_timeout}s")

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    results: list[CompanyBenchmarkResult] = []

    try:
        for i, company in enumerate(companies, start=1):
            print(f"\n[{i}/{len(companies)}] {company}")
            res = run_one_company(session, base_url, company, stage_timeout=args.stage_timeout)
            results.append(res)

            # write JSON after each company
            write_json_snapshot(partial_json, results)

            if res.ok:
                verdict = (res.report_summary or {}).get("verdictLabel", "N/A")
                citations = (res.report_summary or {}).get("citationCount", "N/A")
                print(f"  [OK] run_id={res.run_id} verdict={verdict} citations={citations}")
            else:
                print(f"  [FAIL] failed at stage={res.failure_stage} run_id={res.run_id}")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Caught Ctrl+C. Writing partial summary...")

    finally:
        # always write final summary
        write_json_snapshot(partial_json, results)
        summary = summarize(results)
        print("\n=== Benchmark Summary ===")
        print(json.dumps(summary, indent=2))
        write_outputs(out_dir, results, run_stamp)

if __name__ == "__main__":
    main()