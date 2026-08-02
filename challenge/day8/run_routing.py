"""Day 8 — route ticket classification: small model first, escalate if unsure.

Strategy:
  1) qwen2.5-coder:1.5b — two classify calls (redundancy)
  2) should_escalate(...) heuristics
  3) if unsure → qwen2.5:14b once

Heuristics (explicit):
  - invalid JSON / label not in enum / short reason
  - missing or low confidence score
  - two small-model labels disagree
  - rule: if unsure → escalate
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))

from common.ollama_client import chat  # noqa: E402

DIR = Path(__file__).resolve().parent
LABELS = ("billing", "bug", "feature", "access", "other")
SMALL = "qwen2.5-coder:1.5b"
STRONG = "qwen2.5:14b"

SYSTEM = (
    "Ты классификатор тикетов поддержки. "
    "Ответь ТОЛЬКО валидным JSON без markdown: "
    '{"label":"<enum>","reason":"<одно короткое предложение>","confidence":<0..1>}. '
    "label ∈ billing|bug|feature|access|other. "
    "confidence — твоя уверенность от 0 до 1."
)


def strip_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    return text.strip()


def parse_json_obj(text: str) -> dict[str, Any] | None:
    text = strip_fence(text)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None


def check_constraints(obj: dict[str, Any] | None) -> tuple[bool, list[str]]:
    errs: list[str] = []
    if obj is None:
        return False, ["not_json"]
    if obj.get("label") not in LABELS:
        errs.append(f"bad_label:{obj.get('label')!r}")
    reason = obj.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errs.append("empty_reason")
    elif len(reason.strip()) < 5:
        errs.append("reason_too_short")
    conf = obj.get("confidence")
    if conf is None:
        errs.append("missing_confidence")
    else:
        try:
            c = float(conf)
            if c < 0 or c > 1:
                errs.append("confidence_out_of_range")
        except (TypeError, ValueError):
            errs.append("confidence_not_number")
    return len(errs) == 0, errs


def classify(text: str, model: str, temperature: float = 0.1) -> tuple[dict[str, Any] | None, str, float]:
    content, dt, _ = chat(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        model=model,
        temperature=temperature,
        num_predict=120,
        timeout=300,
    )
    return parse_json_obj(content), content, dt


def should_escalate(
    *,
    a: dict[str, Any] | None,
    b: dict[str, Any] | None,
    ok_a: bool,
    ok_b: bool,
    errs_a: list[str],
    confidence_threshold: float,
) -> tuple[bool, str]:
    """If not confident on small model — escalate to strong."""
    if not ok_a and not ok_b:
        return True, f"constraints_both_failed:{errs_a}"
    # prefer first valid
    primary = a if ok_a else b
    secondary = b if ok_a else a
    assert primary is not None

    conf = float(primary["confidence"])
    if conf < confidence_threshold:
        return True, f"low_confidence:{conf}"

    lab_a = (a or {}).get("label")
    lab_b = (b or {}).get("label")
    if lab_a in LABELS and lab_b in LABELS and lab_a != lab_b:
        return True, f"redundancy_disagreement:{lab_a}/{lab_b}"

    # reason length heuristic
    if len(str(primary.get("reason") or "")) < 10:
        return True, "short_reason"

    # secondary invalid while primary ok → mild uncertainty
    if ok_a and not ok_b:
        return True, "second_call_invalid"

    _ = secondary  # kept for clarity
    return False, "confident_on_small"


def route_one(
    text: str,
    *,
    small: str,
    strong: str,
    confidence_threshold: float,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    calls = 0
    trace: list[dict[str, Any]] = []

    a, raw_a, dt_a = classify(text, small, temperature=0.1)
    calls += 1
    ok_a, errs_a = check_constraints(a)
    trace.append({"step": "small_1", "model": small, "raw": raw_a, "ok": ok_a, "errs": errs_a, "latency": round(dt_a, 3)})

    b, raw_b, dt_b = classify(text, small, temperature=0.45)
    calls += 1
    ok_b, errs_b = check_constraints(b)
    trace.append({"step": "small_2", "model": small, "raw": raw_b, "ok": ok_b, "errs": errs_b, "latency": round(dt_b, 3)})

    escalate, why = should_escalate(
        a=a,
        b=b,
        ok_a=ok_a,
        ok_b=ok_b,
        errs_a=errs_a,
        confidence_threshold=confidence_threshold,
    )

    primary = a if ok_a else b if ok_b else a
    result: dict[str, Any] = {
        "routed_to": "small",
        "escalated": False,
        "escalate_reason": why,
        "label": (primary or {}).get("label") if primary else None,
        "confidence": (primary or {}).get("confidence") if primary else None,
        "final": primary,
        "small_model": small,
        "strong_model": strong,
        "llm_calls": calls,
        "decision": "ACCEPT" if (ok_a or ok_b) and not escalate else "PENDING",
        "trace": trace,
    }

    if not escalate and (ok_a or ok_b):
        result["latency_sec"] = round(time.perf_counter() - t0, 3)
        result["decision"] = "ACCEPT"
        return result

    sobj, sraw, sdt = classify(text, strong, temperature=0.1)
    calls += 1
    sok, serrs = check_constraints(sobj)
    trace.append({"step": "strong", "model": strong, "raw": sraw, "ok": sok, "errs": serrs, "latency": round(sdt, 3)})
    result["escalated"] = True
    result["routed_to"] = "strong"
    result["llm_calls"] = calls
    result["latency_sec"] = round(time.perf_counter() - t0, 3)
    result["escalate_reason"] = why
    if sok and sobj is not None:
        result["label"] = sobj.get("label")
        result["confidence"] = sobj.get("confidence")
        result["final"] = sobj
        result["decision"] = "ACCEPT"
    else:
        result["decision"] = "REJECT"
        result["escalate_reason"] = why + "|strong_failed"
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Day 8 model routing demo")
    ap.add_argument("--cases", type=Path, default=DIR / "cases.jsonl")
    ap.add_argument("--small", default=SMALL)
    ap.add_argument("--strong", default=STRONG)
    ap.add_argument("--confidence-threshold", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    cases = [json.loads(l) for l in args.cases.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit > 0:
        cases = cases[: args.limit]

    progress_path = DIR / "progress.txt"
    progress_path.write_text("", encoding="utf-8")

    def progress(msg: str) -> None:
        line = msg.rstrip() + "\n"
        print(line, end="", flush=True)
        with progress_path.open("a", encoding="utf-8") as pf:
            pf.write(line)

    results: list[dict[str, Any]] = []
    on_small = on_strong = 0
    progress(f"small={args.small} strong={args.strong} threshold={args.confidence_threshold} n={len(cases)}")

    for i, case in enumerate(cases, start=1):
        progress(f"[{i}/{len(cases)}] {case['id']} ({case['kind']}) ...")
        out = route_one(
            case["text"],
            small=args.small,
            strong=args.strong,
            confidence_threshold=args.confidence_threshold,
        )
        if out["routed_to"] == "small":
            on_small += 1
        else:
            on_strong += 1
        gold = case.get("gold")
        row = {
            "id": case["id"],
            "kind": case["kind"],
            "text": case["text"],
            "expect_route": case.get("expect_route"),
            "gold": gold,
            "label_match_gold": (out.get("label") == gold) if gold else None,
            "routed_to": out["routed_to"],
            "escalated": out["escalated"],
            "escalate_reason": out["escalate_reason"],
            "decision": out["decision"],
            "label": out.get("label"),
            "confidence": out.get("confidence"),
            "llm_calls": out["llm_calls"],
            "latency_sec": out["latency_sec"],
            "final": out.get("final"),
            "trace": out["trace"],
        }
        results.append(row)
        progress(
            f"[{i}/{len(cases)}] {case['id']} -> {out['routed_to'].upper()} "
            f"label={out.get('label')} why={out['escalate_reason']} "
            f"t={out['latency_sec']}s (small={on_small} strong={on_strong})"
        )

    n = len(results) or 1
    metrics = {
        "small_model": args.small,
        "strong_model": args.strong,
        "confidence_threshold": args.confidence_threshold,
        "cases": len(results),
        "stayed_on_small": on_small,
        "escalated_to_strong": on_strong,
        "small_share": round(on_small / n, 3),
        "llm_calls_total": sum(r["llm_calls"] for r in results),
        "latency_total_sec": round(sum(r["latency_sec"] for r in results), 2),
        "latency_avg_sec": round(sum(r["latency_sec"] for r in results) / n, 2),
        "by_kind": {},
    }
    for kind in sorted({r["kind"] for r in results}):
        sub = [r for r in results if r["kind"] == kind]
        metrics["by_kind"][kind] = {
            "n": len(sub),
            "small": sum(1 for r in sub if r["routed_to"] == "small"),
            "strong": sum(1 for r in sub if r["routed_to"] == "strong"),
        }

    (DIR / "results.json").write_text(
        json.dumps({"metrics": metrics, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Day 8 — Routing report",
        "",
        f"- Small: `{args.small}` → Strong: `{args.strong}`",
        f"- Confidence threshold: **{args.confidence_threshold}**",
        f"- Cases: **{len(results)}**",
        f"- Stayed on small: **{on_small}** ({100 * on_small / n:.0f}%)",
        f"- Escalated to strong: **{on_strong}** ({100 * on_strong / n:.0f}%)",
        f"- LLM calls: **{metrics['llm_calls_total']}** · avg latency **{metrics['latency_avg_sec']}s**/case",
        "",
        "## Heuristic `should_escalate`",
        "",
        "Escalate if any of:",
        "- invalid JSON / label not in enum / empty reason / missing confidence",
        f"- `confidence` < {args.confidence_threshold}",
        "- two small calls disagree on label",
        "- second small call invalid while first ok",
        "- reason too short",
        "",
        "Otherwise stay on small (**if unsure → escalate**).",
        "",
        "## By kind",
        "",
        "| kind | n | small | strong |",
        "|------|---|-------|--------|",
    ]
    for kind, st in metrics["by_kind"].items():
        lines.append(f"| {kind} | {st['n']} | {st['small']} | {st['strong']} |")

    lines += [
        "",
        "## Per request",
        "",
        "| id | kind | route | label | escalate_reason | s |",
        "|----|------|-------|-------|-----------------|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['kind']} | **{r['routed_to']}** | {r.get('label')} | "
            f"`{r['escalate_reason']}` | {r['latency_sec']} |"
        )
    lines += ["", "Raw: `results.json`. Cases: `cases.jsonl`.", ""]
    (DIR / "ROUTING_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    # sync README threshold note
    progress(f"wrote {DIR / 'results.json'}")
    progress(f"wrote {DIR / 'ROUTING_REPORT.md'}")
    progress(json.dumps(metrics, ensure_ascii=False, indent=2))
    progress("DONE")


if __name__ == "__main__":
    main()
