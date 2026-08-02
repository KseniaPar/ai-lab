"""Day 9 Variant A — monolithic: one big prompt → full JSON."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.ollama_client import chat  # noqa: E402
from common_day9 import field_score, load_cases, parse_json_obj, validate_result  # noqa: E402

DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "qwen2.5-coder:7b"

SYSTEM = (
    "Ты triage-агент поддержки. По тексту тикета верни ОДИН JSON без markdown:\n"
    '{"label":"billing|bug|feature|access|other",'
    '"urgency":"low|medium|high",'
    '"needs_human":true|false,'
    '"reason":"<1 предложение>"}\n'
    "Учитывай сразу категорию, срочность и нужен ли человек. "
    "high/needs_human=true при угрозах, блокировке входа команды, эскалациях, двойных списаниях с давлением."
)


def run_one(text: str, model: str) -> dict:
    t0 = time.perf_counter()
    raw, dt, _ = chat(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        model=model,
        temperature=0.1,
        num_predict=180,
        timeout=300,
    )
    obj = parse_json_obj(raw)
    ok, errs = validate_result(obj)
    return {
        "variant": "monolithic",
        "model": model,
        "raw": raw,
        "result": obj,
        "valid": ok,
        "errors": errs,
        "llm_calls": 1,
        "latency_sec": round(time.perf_counter() - t0, 3),
        "model_latency_sec": round(dt, 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--cases", type=Path, default=DIR / "cases.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", type=Path, default=DIR / "monolithic_results.json")
    args = ap.parse_args()

    cases = load_cases(args.cases)
    if args.limit:
        cases = cases[: args.limit]

    rows = []
    for i, case in enumerate(cases, 1):
        print(f"[mono {i}/{len(cases)}] {case['id']} ...", flush=True)
        out = run_one(case["text"], args.model)
        scores = field_score(out["result"], case["gold"])
        row = {"id": case["id"], "text": case["text"], "gold": case["gold"], "scores": scores, **out}
        rows.append(row)
        print(
            f"  valid={out['valid']} label={ (out['result'] or {}).get('label') } "
            f"scores={scores} t={out['latency_sec']}s",
            flush=True,
        )

    n = len(rows) or 1
    summary = {
        "variant": "monolithic",
        "model": args.model,
        "cases": len(rows),
        "valid_rate": round(sum(1 for r in rows if r["valid"]) / n, 3),
        "label_acc": round(sum(1 for r in rows if r["scores"]["label"]) / n, 3),
        "urgency_acc": round(sum(1 for r in rows if r["scores"]["urgency"]) / n, 3),
        "needs_human_acc": round(sum(1 for r in rows if r["scores"]["needs_human"]) / n, 3),
        "all_fields_acc": round(
            sum(1 for r in rows if all(r["scores"].values())) / n, 3
        ),
        "llm_calls_total": sum(r["llm_calls"] for r in rows),
        "latency_total_sec": round(sum(r["latency_sec"] for r in rows), 2),
        "latency_avg_sec": round(sum(r["latency_sec"] for r in rows) / n, 2),
    }
    args.out.write_text(
        json.dumps({"summary": summary, "results": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
