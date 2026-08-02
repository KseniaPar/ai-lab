"""Run day7 cases one-by-one (short processes) and write METRICS/results."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
CASES = DIR / "cases.jsonl"
OUT = DIR / "results.json"
PARTIAL = DIR / "results.partial.json"
WORKER = DIR / "_case_worker.py"

WORKER.write_text(
    r'''
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))
# load run_confidence as a module by path
import importlib.util
spec = importlib.util.spec_from_file_location(
    "run_confidence", Path(__file__).resolve().parent / "run_confidence.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

case = json.loads(sys.argv[1])
redundancy = int(sys.argv[2])
model = sys.argv[3]
try:
    out = mod.run_pipeline(case["text"], model=model, redundancy_n=redundancy)
except Exception as exc:
    out = {
        "decision": "REJECT",
        "label": None,
        "final": None,
        "reason": f"pipeline_error:{type(exc).__name__}",
        "llm_calls": 0,
        "retries": 0,
        "latency_sec": 0.0,
        "trace": [{"step": "error", "error": str(exc)}],
    }
gold = case.get("gold")
row = {
    "id": case["id"],
    "kind": case["kind"],
    "gold": gold,
    "label_match_gold": (gold is None or out.get("label") == gold) if gold is not None else None,
    **{k: out[k] for k in ("decision", "label", "reason", "llm_calls", "retries", "latency_sec", "final")},
    "trace": out["trace"],
}
print(json.dumps(row, ensure_ascii=False))
''',
    encoding="utf-8",
)


def load_cases() -> list[dict]:
    rows = []
    with CASES.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_metrics(results: list[dict], model: str) -> None:
    n = len(results) or 1
    accepted = sum(1 for r in results if r["decision"] == "ACCEPT")
    rejected = sum(1 for r in results if r["decision"] == "REJECT")
    retry_total = sum(r["retries"] for r in results)
    calls_total = sum(r["llm_calls"] for r in results)
    latency_total = sum(r["latency_sec"] for r in results)
    metrics = {
        "model": model,
        "cases": len(results),
        "accepted": accepted,
        "rejected": rejected,
        "reject_rate": round(rejected / n, 3),
        "cases_with_retry": sum(1 for r in results if r["retries"] > 0),
        "retries_total": retry_total,
        "llm_calls_total": calls_total,
        "llm_calls_avg": round(calls_total / n, 2),
        "latency_total_sec": round(latency_total, 2),
        "latency_avg_sec": round(latency_total / n, 2),
        "cost_proxy": "llm_calls (local Ollama; no $)",
        "by_kind": {},
    }
    for kind in ("correct", "borderline", "noisy"):
        subset = [r for r in results if r["kind"] == kind]
        if not subset:
            continue
        metrics["by_kind"][kind] = {
            "n": len(subset),
            "accepted": sum(1 for r in subset if r["decision"] == "ACCEPT"),
            "rejected": sum(1 for r in subset if r["decision"] == "REJECT"),
        }
    OUT.write_text(
        json.dumps({"metrics": metrics, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Day 7 — Confidence metrics",
        "",
        f"- Model: `{metrics['model']}`",
        f"- Cases: **{metrics['cases']}**",
        f"- ACCEPT: **{metrics['accepted']}** · REJECT: **{metrics['rejected']}** (reject rate {metrics['reject_rate']:.0%})",
        f"- Cases with retry (constraint re-infer): **{metrics['cases_with_retry']}** (retries total {metrics['retries_total']})",
        f"- LLM calls: **{metrics['llm_calls_total']}** total · avg **{metrics['llm_calls_avg']}**/case",
        f"- Latency: **{metrics['latency_total_sec']}s** total · avg **{metrics['latency_avg_sec']}s**/case",
        f"- Cost proxy: number of LLM calls (local Ollama, $0 cloud)",
        "",
        "## By kind",
        "",
        "| kind | n | ACCEPT | REJECT |",
        "|------|---|--------|--------|",
    ]
    for kind, st in metrics["by_kind"].items():
        lines.append(f"| {kind} | {st['n']} | {st['accepted']} | {st['rejected']} |")
    lines += [
        "",
        "## Approaches used",
        "",
        "1. **Constraint-based** — input signal + JSON parse, label ∈ enum, reason length",
        "2. **Redundancy** — independent classify calls, majority ≥2",
        "3. **Self-check** — second model pass OK / FIX / UNSURE",
        "",
        "Raw: `results.json`. Cases: `cases.jsonl`.",
        "",
    ]
    (DIR / "METRICS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def main() -> None:
    model = "qwen2.5-coder:7b"
    redundancy = 2
    cases = load_cases()
    results: list[dict] = []
    for i, case in enumerate(cases, start=1):
        print(f"[{i}/{len(cases)}] {case['id']} ...", flush=True)
        proc = subprocess.run(
            [sys.executable, "-u", str(WORKER), json.dumps(case, ensure_ascii=False), str(redundancy), model],
            cwd=str(DIR.parent.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if proc.returncode != 0:
            print(proc.stderr[-500:], flush=True)
            row = {
                "id": case["id"],
                "kind": case["kind"],
                "gold": case.get("gold"),
                "label_match_gold": None,
                "decision": "REJECT",
                "label": None,
                "reason": f"worker_exit:{proc.returncode}",
                "llm_calls": 0,
                "retries": 0,
                "latency_sec": 0.0,
                "final": None,
                "trace": [{"step": "error", "stderr": proc.stderr[-300:]}],
            }
        else:
            # last line is JSON
            line = [ln for ln in proc.stdout.splitlines() if ln.strip().startswith("{")][-1]
            row = json.loads(line)
        results.append(row)
        PARTIAL.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"  -> {row['decision']} label={row.get('label')} why={row['reason']} "
            f"calls={row['llm_calls']} t={row['latency_sec']}s",
            flush=True,
        )
    write_metrics(results, model)
    print(f"wrote {OUT}", flush=True)
    print(f"wrote {DIR / 'METRICS.md'}", flush=True)


if __name__ == "__main__":
    main()
