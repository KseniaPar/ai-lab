"""Run baseline: first 10 eval examples through base Ollama model (no fine-tune)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))

from common.ollama_client import chat  # noqa: E402

DIR = Path(__file__).resolve().parent
EVAL = DIR / "dataset" / "eval.jsonl"
OUT_DIR = DIR / "baseline"
LABELS = {"billing", "bug", "feature", "access", "other"}


def parse_label(text: str) -> str | None:
    text = text.strip()
    # strip markdown fences if any
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    try:
        obj = json.loads(text)
        label = obj.get("label")
        return label if label in LABELS else None
    except json.JSONDecodeError:
        for lab in LABELS:
            if f'"{lab}"' in text or f"'{lab}'" in text:
                return lab
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5-coder:7b")
    ap.add_argument("--n", type=int, default=10)
    args = ap.parse_args()

    rows = []
    with EVAL.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    sample = rows[: args.n]
    if len(sample) < args.n:
        raise SystemExit(f"eval has only {len(sample)} rows, need {args.n}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "baseline_responses.jsonl"
    summary_path = OUT_DIR / "SUMMARY.md"

    results = []
    correct = 0
    valid_json = 0

    with out_path.open("w", encoding="utf-8") as out:
        for i, ex in enumerate(sample, start=1):
            msgs = ex["messages"]
            gold = json.loads(msgs[2]["content"])
            prompt_msgs = [
                {"role": msgs[0]["role"], "content": msgs[0]["content"]},
                {"role": msgs[1]["role"], "content": msgs[1]["content"]},
            ]
            print(f"[{i}/{len(sample)}] calling {args.model}…")
            content, latency, _ = chat(prompt_msgs, model=args.model, temperature=0.1)
            pred = parse_label(content)
            ok_json = pred is not None
            match = pred == gold["label"]
            if ok_json:
                valid_json += 1
            if match:
                correct += 1
            row = {
                "id": i,
                "user": msgs[1]["content"],
                "gold_label": gold["label"],
                "pred_label": pred,
                "match": match,
                "valid_json_label": ok_json,
                "latency_sec": round(latency, 3),
                "model": args.model,
                "raw_response": content,
            }
            results.append(row)
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"  gold={gold['label']} pred={pred} match={match} t={latency:.1f}s")

    lines = [
        f"# Baseline — {args.model}",
        "",
        f"- Samples: **{len(results)}** (from `dataset/eval.jsonl`)",
        f"- Exact label match: **{correct}/{len(results)}** ({100 * correct / len(results):.0f}%)",
        f"- Valid JSON label in enum: **{valid_json}/{len(results)}**",
        f"- Mean latency: **{sum(r['latency_sec'] for r in results) / len(results):.2f}s**",
        "",
        "| # | gold | pred | match | s |",
        "|---|------|------|-------|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['gold_label']} | {r['pred_label']} | "
            f"{'Y' if r['match'] else 'N'} | {r['latency_sec']} |"
        )
    lines.append("")
    lines.append("Raw responses: `baseline_responses.jsonl`. Criteria: `CRITERIA.md`.")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"wrote {summary_path}")
    print(f"accuracy {correct}/{len(results)}")


if __name__ == "__main__":
    main()
