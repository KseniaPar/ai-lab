"""Day 9 Variant B — multi-stage: normalize → classify → decide → assemble.

Each stage: short strict JSON. Cheap models + rule stage for decide.
"""
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
from common_day9 import (  # noqa: E402
    LABELS,
    decide_urgency_rules,
    field_score,
    load_cases,
    parse_json_obj,
    validate_result,
)

DIR = Path(__file__).resolve().parent
MODEL_NORM = "qwen2.5-coder:1.5b"
MODEL_CLF = "qwen2.5-coder:7b"

SYS_NORM = (
    "Нормализуй тикет. Верни ТОЛЬКО compact JSON: "
    '{"clean":"<1-2 предложения, суть без эмоций и капса>"}'
)
SYS_CLF = (
    "Классифицируй тикет. Верни ТОЛЬКО compact JSON: "
    '{"label":"billing|bug|feature|access|other"}'
)


def stage_normalize(text: str, model: str) -> tuple[dict | None, str, float]:
    raw, dt, _ = chat(
        [{"role": "system", "content": SYS_NORM}, {"role": "user", "content": text}],
        model=model,
        temperature=0.1,
        num_predict=80,
        timeout=300,
    )
    obj = parse_json_obj(raw)
    if obj and isinstance(obj.get("clean"), str) and obj["clean"].strip():
        return obj, raw, dt
    # fallback: truncated original
    return {"clean": text.strip()[:240]}, raw, dt


def stage_classify(clean: str, model: str) -> tuple[dict | None, str, float]:
    raw, dt, _ = chat(
        [{"role": "system", "content": SYS_CLF}, {"role": "user", "content": clean}],
        model=model,
        temperature=0.1,
        num_predict=40,
        timeout=300,
    )
    obj = parse_json_obj(raw)
    if obj and obj.get("label") in LABELS:
        return {"label": obj["label"]}, raw, dt
    return None, raw, dt


def stage_decide(clean: str, label: str) -> dict:
    """Stage 3: no LLM — strict enum from rules (cheap & deterministic)."""
    return decide_urgency_rules(clean, label)


def stage_assemble(clean: str, label: str, decision: dict) -> dict:
    reason = f"{label}; urgency={decision['urgency']}; human={decision['needs_human']}"
    return {
        "label": label,
        "urgency": decision["urgency"],
        "needs_human": decision["needs_human"],
        "reason": reason,
        "clean": clean,
    }


def run_one(text: str, model_norm: str, model_clf: str) -> dict:
    t0 = time.perf_counter()
    calls = 0
    trace = []

    norm, raw_n, dt_n = stage_normalize(text, model_norm)
    calls += 1
    clean = norm["clean"]
    trace.append({"stage": 1, "name": "normalize", "model": model_norm, "out": norm, "latency": round(dt_n, 3)})

    clf, raw_c, dt_c = stage_classify(clean, model_clf)
    calls += 1
    trace.append({"stage": 2, "name": "classify", "model": model_clf, "raw": raw_c, "out": clf, "latency": round(dt_c, 3)})

    if clf is None:
        assembled = None
        ok, errs = False, ["classify_failed"]
    else:
        decision = stage_decide(clean, clf["label"])
        trace.append({"stage": 3, "name": "decide", "model": "rules", "out": decision, "latency": 0.0})
        assembled = stage_assemble(clean, clf["label"], decision)
        trace.append({"stage": 4, "name": "assemble", "model": "none", "out": assembled, "latency": 0.0})
        ok, errs = validate_result(assembled)

    return {
        "variant": "multi_stage",
        "models": {"normalize": model_norm, "classify": model_clf, "decide": "rules"},
        "result": assembled,
        "valid": ok,
        "errors": errs,
        "llm_calls": calls,
        "latency_sec": round(time.perf_counter() - t0, 3),
        "trace": trace,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-norm", default=MODEL_NORM)
    ap.add_argument("--model-clf", default=MODEL_CLF)
    ap.add_argument("--cases", type=Path, default=DIR / "cases.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", type=Path, default=DIR / "multistage_results.json")
    args = ap.parse_args()

    cases = load_cases(args.cases)
    if args.limit:
        cases = cases[: args.limit]

    rows = []
    for i, case in enumerate(cases, 1):
        print(f"[multi {i}/{len(cases)}] {case['id']} ...", flush=True)
        out = run_one(case["text"], args.model_norm, args.model_clf)
        scores = field_score(out["result"], case["gold"])
        row = {"id": case["id"], "text": case["text"], "gold": case["gold"], "scores": scores, **out}
        rows.append(row)
        print(
            f"  valid={out['valid']} label={(out['result'] or {}).get('label')} "
            f"scores={scores} calls={out['llm_calls']} t={out['latency_sec']}s",
            flush=True,
        )

    n = len(rows) or 1
    summary = {
        "variant": "multi_stage",
        "models": {"normalize": args.model_norm, "classify": args.model_clf, "decide": "rules"},
        "cases": len(rows),
        "valid_rate": round(sum(1 for r in rows if r["valid"]) / n, 3),
        "label_acc": round(sum(1 for r in rows if r["scores"]["label"]) / n, 3),
        "urgency_acc": round(sum(1 for r in rows if r["scores"]["urgency"]) / n, 3),
        "needs_human_acc": round(sum(1 for r in rows if r["scores"]["needs_human"]) / n, 3),
        "all_fields_acc": round(sum(1 for r in rows if all(r["scores"].values())) / n, 3),
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
