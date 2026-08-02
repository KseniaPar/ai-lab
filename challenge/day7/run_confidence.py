"""Day 7 — confidence / quality gate for ticket classification (no fine-tune).

Approaches:
  1) Constraint-based — JSON / enum / reason length
  2) Self-check — second pass verifies or fixes label
  3) Redundancy — 2–3 independent calls, majority vote

Decision: ACCEPT | RETRY | REJECT
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))

from common.ollama_client import chat  # noqa: E402

DIR = Path(__file__).resolve().parent
LABELS = ("billing", "bug", "feature", "access", "other")
SYSTEM = (
    "Ты классификатор тикетов поддержки. "
    "Ответь ТОЛЬКО валидным JSON без markdown: "
    '{"label":"<enum>","reason":"<одно короткое предложение>"}. '
    "label ∈ billing|bug|feature|access|other."
)
SELF_CHECK_SYSTEM = (
    "Ты проверяешь классификацию тикета. "
    "Дан текст тикета и предложенный JSON. "
    "Если текст бессмысленный, слишком короткий по смыслу, троллинг или не содержит "
    "конкретной проблемы — верни "
    '{"verdict":"UNSURE","label":null,"reason":"<кратко>"}. '
    "Если label верен и уверенность высокая — верни "
    '{"verdict":"OK","label":"<тот же>","reason":"<кратко>"}. '
    "Если label сомнителен или неверен, но текст осмысленный — "
    '{"verdict":"FIX","label":"<исправленный>","reason":"<кратко>"}. '
    "Только JSON, без markdown."
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


# --- 1) Constraint-based -------------------------------------------------

def check_constraints(obj: dict[str, Any] | None) -> tuple[bool, list[str]]:
    errs: list[str] = []
    if obj is None:
        return False, ["not_json"]
    label = obj.get("label")
    reason = obj.get("reason")
    if label not in LABELS:
        errs.append(f"bad_label:{label!r}")
    if not isinstance(reason, str) or not reason.strip():
        errs.append("empty_reason")
    elif len(reason.strip()) > 200:
        errs.append("reason_too_long")
    elif len(reason.strip()) < 5:
        errs.append("reason_too_short")
    return (len(errs) == 0), errs


# --- classify once -------------------------------------------------------

def classify_once(
    text: str,
    *,
    model: str,
    temperature: float = 0.2,
) -> tuple[dict[str, Any] | None, str, float]:
    content, latency, _ = chat(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
        model=model,
        temperature=temperature,
        num_predict=128,
    )
    return parse_json_obj(content), content, latency


# --- 2) Self-check -------------------------------------------------------

def self_check(
    text: str,
    candidate: dict[str, Any],
    *,
    model: str,
) -> tuple[dict[str, Any] | None, str, float]:
    payload = json.dumps(candidate, ensure_ascii=False)
    content, latency, _ = chat(
        [
            {"role": "system", "content": SELF_CHECK_SYSTEM},
            {
                "role": "user",
                "content": f"Тикет:\n{text}\n\nПредложенный ответ:\n{payload}",
            },
        ],
        model=model,
        temperature=0.1,
        num_predict=128,
    )
    return parse_json_obj(content), content, latency


# --- 3) Redundancy -------------------------------------------------------

def redundancy_vote(
    text: str,
    *,
    model: str,
    n: int = 3,
) -> tuple[str | None, list[str], list[float], bool]:
    """Returns (majority_label, labels, latencies, unanimous_enough)."""
    labels: list[str] = []
    latencies: list[float] = []
    for i in range(n):
        obj, _, dt = classify_once(text, model=model, temperature=0.4 + 0.15 * i)
        latencies.append(dt)
        ok, _ = check_constraints(obj)
        if ok and obj is not None:
            labels.append(str(obj["label"]))
        else:
            labels.append("INVALID")
    counted = Counter(lab for lab in labels if lab != "INVALID")
    if not counted:
        return None, labels, latencies, False
    top, votes = counted.most_common(1)[0]
    # accept majority if ≥2 agree (for n=3) or all valid agree
    unanimous_enough = votes >= 2
    return (top if unanimous_enough else None), labels, latencies, unanimous_enough


# --- input signal (constraint-based, no LLM) -----------------------------

def insufficient_signal(text: str) -> tuple[bool, str]:
    """Reject obvious noise before spending LLM calls."""
    t = text.strip()
    if len(t) < 12:
        return True, "too_short"
    letters = sum(1 for c in t if c.isalpha())
    if letters < 12:
        return True, "too_few_letters"
    if letters / max(len(t), 1) < 0.35:
        return True, "low_letter_ratio"
    low = t.lower()
    label_hits = sum(1 for lab in LABELS if lab in low)
    if label_hits >= 3:
        return True, "all_labels_stuffed"
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ]{3,}", t)
    if len(tokens) <= 2:
        return True, "too_few_tokens"
    # keyboard-mash / placeholder noise
    mash = {"asdf", "qwerty", "qwert", "lorem", "ipsum", "test", "testing", "xxx", "aaa", "bbbb"}
    alpha_tokens = [tok.lower() for tok in tokens]
    if sum(1 for tok in alpha_tokens if tok in mash) >= 2:
        return True, "placeholder_noise"
    return False, ""


# --- pipeline ------------------------------------------------------------

def run_pipeline(text: str, *, model: str, redundancy_n: int = 3) -> dict[str, Any]:
    """Full gate: constraints → redundancy → self-check → decision."""
    t0 = time.perf_counter()
    calls = 0
    retries = 0
    trace: list[dict[str, Any]] = []

    bad, why = insufficient_signal(text)
    trace.append({"step": "input_signal", "insufficient": bad, "why": why})
    if bad:
        return _result("REJECT", None, calls, retries, t0, trace, reason=f"insufficient_signal:{why}")

    # Primary classify
    obj, raw, dt = classify_once(text, model=model, temperature=0.1)
    calls += 1
    ok, errs = check_constraints(obj)
    trace.append({"step": "classify", "raw": raw, "ok": ok, "errs": errs, "latency": round(dt, 3)})

    if not ok:
        # RETRY once on constraint failure
        retries += 1
        obj2, raw2, dt2 = classify_once(text, model=model, temperature=0.0)
        calls += 1
        ok2, errs2 = check_constraints(obj2)
        trace.append(
            {"step": "retry_classify", "raw": raw2, "ok": ok2, "errs": errs2, "latency": round(dt2, 3)}
        )
        if not ok2:
            return _result(
                "REJECT",
                None,
                calls,
                retries,
                t0,
                trace,
                reason="constraints_failed_after_retry",
            )
        obj = obj2

    assert obj is not None

    # Redundancy
    maj, labs, lats, enough = redundancy_vote(text, model=model, n=redundancy_n)
    calls += redundancy_n
    trace.append(
        {
            "step": "redundancy",
            "labels": labs,
            "majority": maj,
            "enough": enough,
            "latency": round(sum(lats), 3),
        }
    )
    if not enough or maj is None:
        return _result(
            "REJECT",
            obj.get("label"),
            calls,
            retries,
            t0,
            trace,
            reason="redundancy_disagreement",
        )
    if maj != obj["label"]:
        # escalate: take majority, still self-check
        obj = {"label": maj, "reason": obj.get("reason") or f"majority={maj}"}

    # Self-check
    sc, sc_raw, sc_dt = self_check(text, obj, model=model)
    calls += 1
    trace.append({"step": "self_check", "raw": sc_raw, "parsed": sc, "latency": round(sc_dt, 3)})

    if sc is None:
        return _result("REJECT", obj["label"], calls, retries, t0, trace, reason="self_check_unparseable")

    verdict = str(sc.get("verdict") or "").upper()
    if verdict == "UNSURE":
        return _result("REJECT", obj["label"], calls, retries, t0, trace, reason="self_check_unsure")
    if verdict == "FIX":
        new_label = sc.get("label")
        if new_label not in LABELS:
            return _result("REJECT", obj["label"], calls, retries, t0, trace, reason="self_check_bad_fix")
        # one more constraint pass on fixed
        fixed = {"label": new_label, "reason": sc.get("reason") or obj.get("reason")}
        ok_f, errs_f = check_constraints(fixed)
        if not ok_f:
            return _result("REJECT", new_label, calls, retries, t0, trace, reason="fix_constraints_failed")
        # if fix disagrees with majority — reject rather than silently accept
        if new_label != maj:
            return _result(
                "REJECT",
                new_label,
                calls,
                retries,
                t0,
                trace,
                reason="self_check_vs_majority_conflict",
            )
        return _result("ACCEPT", new_label, calls, retries, t0, trace, reason="self_check_fix_ok", final=fixed)

    if verdict == "OK":
        final_label = sc.get("label") or obj["label"]
        if final_label not in LABELS:
            return _result("REJECT", obj["label"], calls, retries, t0, trace, reason="ok_bad_label")
        final = {"label": final_label, "reason": sc.get("reason") or obj.get("reason")}
        return _result("ACCEPT", final_label, calls, retries, t0, trace, reason="self_check_ok", final=final)

    return _result("REJECT", obj["label"], calls, retries, t0, trace, reason=f"unknown_verdict:{verdict}")


def _result(
    decision: str,
    label: Any,
    calls: int,
    retries: int,
    t0: float,
    trace: list[dict[str, Any]],
    *,
    reason: str,
    final: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "decision": decision,
        "label": label,
        "final": final,
        "reason": reason,
        "llm_calls": calls,
        "retries": retries,
        "latency_sec": round(time.perf_counter() - t0, 3),
        "trace": trace,
    }


def load_cases(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> None:
    # Windows consoles often use cp1251 — avoid UnicodeEncodeError on prints
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Day 7 confidence gate demo")
    ap.add_argument("--cases", type=Path, default=DIR / "cases.jsonl")
    ap.add_argument("--model", default="qwen2.5-coder:7b")
    ap.add_argument("--redundancy", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="0 = all cases")
    args = ap.parse_args()

    cases = load_cases(args.cases)
    if args.limit > 0:
        cases = cases[: args.limit]

    results: list[dict[str, Any]] = []
    accepted = rejected = 0
    retry_total = 0
    calls_total = 0
    latency_total = 0.0

    progress_path = DIR / "progress.txt"

    def progress(msg: str) -> None:
        line = msg.rstrip() + "\n"
        print(line, end="", flush=True)
        with progress_path.open("a", encoding="utf-8") as pf:
            pf.write(line)
            pf.flush()

    progress_path.write_text("", encoding="utf-8")
    progress(f"model={args.model} cases={len(cases)} redundancy={args.redundancy}")
    for i, case in enumerate(cases, start=1):
        progress(f"[{i}/{len(cases)}] {case['id']} ({case['kind']}) starting...")
        try:
            out = run_pipeline(case["text"], model=args.model, redundancy_n=args.redundancy)
        except Exception as exc:  # noqa: BLE001
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
            progress(f"[{i}/{len(cases)}] {case['id']} ERROR: {exc}")
        gold = case.get("gold")
        label_ok = gold is None or out.get("label") == gold
        row = {
            "id": case["id"],
            "kind": case["kind"],
            "gold": gold,
            "label_match_gold": label_ok if gold is not None else None,
            **{k: out[k] for k in ("decision", "label", "reason", "llm_calls", "retries", "latency_sec", "final")},
            "trace": out["trace"],
        }
        results.append(row)
        if out["decision"] == "ACCEPT":
            accepted += 1
        else:
            rejected += 1
        retry_total += out["retries"]
        calls_total += out["llm_calls"]
        latency_total += out["latency_sec"]
        progress(
            f"[{i}/{len(cases)}] {case['id']} -> {out['decision']} "
            f"label={out.get('label')} why={out['reason']} "
            f"calls={out['llm_calls']} t={out['latency_sec']}s "
            f"(done {i}/{len(cases)}, ACCEPT={accepted} REJECT={rejected})"
        )
        (DIR / "results.partial.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    n = len(results) or 1
    metrics = {
        "model": args.model,
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

    out_json = DIR / "results.json"
    out_json.write_text(json.dumps({"metrics": metrics, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

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
        "2. **Redundancy** — 3 independent classify calls, majority ≥2",
        "3. **Self-check** — second model pass OK / FIX / UNSURE",
        "",
        "Raw: `results.json`. Cases: `cases.jsonl`.",
        "",
    ]
    (DIR / "METRICS.md").write_text("\n".join(lines), encoding="utf-8")
    progress(f"wrote {out_json}")
    progress(f"wrote {DIR / 'METRICS.md'}")
    progress(json.dumps(metrics, ensure_ascii=False, indent=2))
    progress("DONE")


if __name__ == "__main__":
    main()
