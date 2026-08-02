"""Day 10 — micro-model first (embeddings kNN) → LLM fallback.

Micro: nomic-embed-text + cosine kNN over day6 train.
Returns label + confidence + status OK|UNSURE.
Big LLM (qwen2.5-coder:7b) only on UNSURE / low conf / bad format.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))

from common.ollama_client import chat  # noqa: E402

DIR = Path(__file__).resolve().parent
LABELS = ("billing", "bug", "feature", "access", "other")
EMBED_MODEL = "nomic-embed-text"
BIG_MODEL = "qwen2.5-coder:7b"
HOST = "http://127.0.0.1:11434"

SYSTEM = (
    "Ты классификатор тикетов поддержки. "
    "Ответь ТОЛЬКО валидным JSON без markdown: "
    '{"label":"<enum>","reason":"<одно короткое предложение>"}. '
    "label ∈ billing|bug|feature|access|other."
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


def embed(text: str, model: str = EMBED_MODEL) -> list[float]:
    body = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{HOST}/api/embeddings",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    vec = payload.get("embedding")
    if not vec:
        raise RuntimeError("empty embedding")
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [float(x) / n for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def load_index(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["items"]


def micro_classify(
    text: str,
    index: list[dict[str, Any]],
    *,
    k: int = 5,
    ok_threshold: float = 0.72,
    margin_threshold: float = 0.03,
) -> dict[str, Any]:
    """Embedding kNN micro-model → label, confidence, status OK|UNSURE."""
    t0 = time.perf_counter()
    # garbage / no signal
    letters = sum(1 for c in text if c.isalpha())
    if letters < 12:
        return {
            "label": None,
            "confidence": 0.0,
            "status": "UNSURE",
            "reason": "insufficient_signal",
            "latency_sec": round(time.perf_counter() - t0, 3),
            "neighbors": [],
        }

    q = embed(text)
    scored = []
    for item in index:
        scored.append((cosine(q, item["vector"]), item["label"], item["text"][:80]))
    scored.sort(reverse=True)
    top = scored[:k]
    # majority among top-k weighted by similarity
    votes: dict[str, float] = {}
    for sim, lab, _ in top:
        votes[lab] = votes.get(lab, 0.0) + max(sim, 0.0)
    label = max(votes, key=votes.get)
    best_sim = top[0][0]
    # margin: best label score vs second label
    ordered = sorted(votes.values(), reverse=True)
    margin = ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0)
    confidence = round(0.5 * best_sim + 0.5 * min(1.0, margin * 5), 4)

    status = "OK"
    why = "knn_ok"
    if best_sim < ok_threshold:
        status = "UNSURE"
        why = f"low_sim:{best_sim:.3f}"
    elif margin < margin_threshold:
        status = "UNSURE"
        why = f"low_margin:{margin:.3f}"
    elif label not in LABELS:
        status = "UNSURE"
        why = "bad_label"

    return {
        "label": label if label in LABELS else None,
        "confidence": confidence,
        "status": status,
        "reason": why,
        "best_sim": round(best_sim, 4),
        "margin": round(margin, 4),
        "latency_sec": round(time.perf_counter() - t0, 3),
        "neighbors": [{"sim": round(s, 4), "label": lab, "text": tx} for s, lab, tx in top[:3]],
    }


def llm_fallback(text: str, model: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    raw, dt, _ = chat(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
        model=model,
        temperature=0.1,
        num_predict=100,
        timeout=300,
    )
    obj = parse_json_obj(raw)
    ok = bool(obj and obj.get("label") in LABELS)
    return {
        "label": obj.get("label") if ok else None,
        "raw": raw,
        "valid": ok,
        "latency_sec": round(time.perf_counter() - t0, 3),
        "model_latency_sec": round(dt, 3),
        "model": model,
    }


def pipeline(
    text: str,
    index: list[dict[str, Any]],
    *,
    big_model: str,
    ok_threshold: float,
    margin_threshold: float,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    micro = micro_classify(
        text, index, ok_threshold=ok_threshold, margin_threshold=margin_threshold
    )
    used_fallback = False
    big_calls = 0
    final_label = micro.get("label")
    source = "micro"

    need_fallback = (
        micro["status"] == "UNSURE"
        or micro.get("label") not in LABELS
        or micro.get("confidence", 0) < 0.55
    )
    fallback = None
    if need_fallback:
        used_fallback = True
        big_calls = 1
        fallback = llm_fallback(text, big_model)
        if fallback["valid"]:
            final_label = fallback["label"]
            source = "llm_fallback"
        else:
            source = "failed"

    return {
        "label": final_label,
        "source": source,
        "micro": micro,
        "fallback": fallback,
        "used_fallback": used_fallback,
        "big_llm_calls": big_calls,
        "latency_sec": round(time.perf_counter() - t0, 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Day 10 micro-first pipeline")
    ap.add_argument("--cases", type=Path, default=DIR / "cases.jsonl")
    ap.add_argument("--index", type=Path, default=DIR / "index.json")
    ap.add_argument("--big-model", default=BIG_MODEL)
    ap.add_argument("--ok-threshold", type=float, default=0.72)
    ap.add_argument("--margin-threshold", type=float, default=0.03)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if not args.index.is_file():
        print("index missing — run build_index.py first", file=sys.stderr)
        raise SystemExit(1)

    index = load_index(args.index)
    cases = [json.loads(l) for l in args.cases.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        cases = cases[: args.limit]

    progress = DIR / "progress.txt"
    progress.write_text("", encoding="utf-8")

    def log(msg: str) -> None:
        line = msg.rstrip() + "\n"
        print(line, end="", flush=True)
        with progress.open("a", encoding="utf-8") as f:
            f.write(line)

    results = []
    micro_ok = fallback_n = big_calls = 0
    lat_sum = 0.0
    log(f"index={len(index)} cases={len(cases)} big={args.big_model} thr={args.ok_threshold}")

    for i, case in enumerate(cases, 1):
        log(f"[{i}/{len(cases)}] {case['id']} ({case['kind']}) ...")
        out = pipeline(
            case["text"],
            index,
            big_model=args.big_model,
            ok_threshold=args.ok_threshold,
            margin_threshold=args.margin_threshold,
        )
        if out["used_fallback"]:
            fallback_n += 1
        else:
            micro_ok += 1
        big_calls += out["big_llm_calls"]
        lat_sum += out["latency_sec"]
        gold = case.get("gold")
        row = {
            "id": case["id"],
            "kind": case["kind"],
            "text": case["text"],
            "gold": gold,
            "label_match_gold": (out["label"] == gold) if gold else None,
            **out,
        }
        results.append(row)
        log(
            f"[{i}/{len(cases)}] {case['id']} -> {out['source']} "
            f"label={out['label']} micro={out['micro']['status']}/"
            f"{out['micro']['confidence']} t={out['latency_sec']}s "
            f"(micro_handled={micro_ok} fallback={fallback_n})"
        )

    n = len(results) or 1
    metrics = {
        "micro": "nomic-embed-text kNN",
        "big_model": args.big_model,
        "cases": len(results),
        "micro_handled": micro_ok,
        "fallback": fallback_n,
        "micro_share": round(micro_ok / n, 3),
        "big_llm_calls_total": big_calls,
        "latency_total_sec": round(lat_sum, 2),
        "latency_avg_sec": round(lat_sum / n, 2),
        "by_kind": {},
    }
    for kind in ("simple", "borderline", "hard"):
        sub = [r for r in results if r["kind"] == kind]
        if not sub:
            continue
        metrics["by_kind"][kind] = {
            "n": len(sub),
            "micro": sum(1 for r in sub if not r["used_fallback"]),
            "fallback": sum(1 for r in sub if r["used_fallback"]),
            "label_acc": round(
                sum(1 for r in sub if r.get("gold") and r["label"] == r["gold"])
                / max(1, sum(1 for r in sub if r.get("gold"))),
                3,
            ),
        }

    (DIR / "results.json").write_text(
        json.dumps({"metrics": metrics, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Day 10 — Micro-model first metrics",
        "",
        f"- Micro: **nomic-embed-text** kNN over day6 train (`index.json`)",
        f"- Big LLM fallback: `{args.big_model}`",
        f"- Cases: **{len(results)}**",
        f"- Handled by micro only: **{micro_ok}** ({100 * micro_ok / n:.0f}%)",
        f"- Went to LLM fallback: **{fallback_n}** ({100 * fallback_n / n:.0f}%)",
        f"- Big LLM calls total: **{big_calls}**",
        f"- Latency avg: **{metrics['latency_avg_sec']}s**/case (total {metrics['latency_total_sec']}s)",
        "",
        "## By kind",
        "",
        "| kind | n | micro | fallback | label acc |",
        "|------|---|-------|----------|-----------|",
    ]
    for kind, st in metrics["by_kind"].items():
        lines.append(
            f"| {kind} | {st['n']} | {st['micro']} | {st['fallback']} | {st['label_acc']:.0%} |"
        )
    lines += [
        "",
        "## Gate to fallback",
        "",
        "- micro status `UNSURE`",
        f"- best cosine sim < {args.ok_threshold} or label-margin < {args.margin_threshold}",
        "- confidence < 0.55 or invalid label",
        "",
        "Raw: `results.json`. Cases: `cases.jsonl`.",
        "",
    ]
    (DIR / "METRICS.md").write_text("\n".join(lines), encoding="utf-8")
    log(f"wrote {DIR / 'results.json'}")
    log(f"wrote {DIR / 'METRICS.md'}")
    log(json.dumps(metrics, ensure_ascii=False, indent=2))
    log("DONE")


if __name__ == "__main__":
    main()
