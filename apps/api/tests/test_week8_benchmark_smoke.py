from pathlib import Path
import json
import subprocess
import sys


def test_week8_benchmark_smoke():
    out_dir = Path("artifacts/week8_test")
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "scripts/run_week8_benchmark.py",
        "--base-url",
        "http://127.0.0.1:8000",
        "--companies-file",
        "apps/api/tests/fixtures/week8_companies.json",
        "--max-companies",
        "2",
        "--out-dir",
        str(out_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout

    files = sorted(out_dir.glob("week8_benchmark_*.json"))
    assert files, "No benchmark JSON artifact generated"

    payload = json.loads(files[-1].read_text(encoding="utf-8"))
    assert "summary" in payload
    assert "results" in payload
    assert payload["summary"]["totalCompanies"] == 2