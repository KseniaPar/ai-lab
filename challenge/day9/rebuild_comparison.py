"""Rebuild COMPARISON.md from existing mono/multi result JSONs."""
from __future__ import annotations

import json
from pathlib import Path

DIR = Path(__file__).resolve().parent


def main() -> None:
    mono = json.loads((DIR / "monolithic_results.json").read_text(encoding="utf-8"))
    multi = json.loads((DIR / "multistage_results.json").read_text(encoding="utf-8"))
    sm, su = mono["summary"], multi["summary"]
    lines = [
        "# Day 9 — Monolithic vs Multi-stage",
        "",
        "Задача: из одного тикета извлечь **несколько полей** — "
        "`label`, `urgency`, `needs_human`, `reason` (плохо одним запросом).",
        "",
        "## Variants",
        "",
        "| | Monolithic (A) | Multi-stage (B) |",
        "|-|----------------|-----------------|",
        f"| Models | `{sm['model']}` x1 | norm `{su['models']['normalize']}` + "
        f"clf `{su['models']['classify']}` + decide **rules** |",
        "| LLM calls / case | 1 | 2 (+0 rules) |",
        f"| Cases | {sm['cases']} | {su['cases']} |",
        f"| Valid JSON | {sm['valid_rate']:.0%} | {su['valid_rate']:.0%} |",
        f"| label acc | {sm['label_acc']:.0%} | {su['label_acc']:.0%} |",
        f"| urgency acc | {sm['urgency_acc']:.0%} | {su['urgency_acc']:.0%} |",
        f"| needs_human acc | {sm['needs_human_acc']:.0%} | {su['needs_human_acc']:.0%} |",
        f"| all fields | {sm['all_fields_acc']:.0%} | {su['all_fields_acc']:.0%} |",
        f"| LLM calls total | {sm['llm_calls_total']} | {su['llm_calls_total']} |",
        f"| Latency total | {sm['latency_total_sec']}s | {su['latency_total_sec']}s |",
        f"| Latency avg | {sm['latency_avg_sec']}s | {su['latency_avg_sec']}s |",
        "",
        "## Multi-stage pipeline",
        "",
        "1. **normalize** → `{\"clean\":\"...\"}` (1.5b, short)",
        "2. **classify** → `{\"label\":\"enum\"}` (7b, short)",
        "3. **decide** → `{\"urgency\":\"low|medium|high\",\"needs_human\":bool}` (rules, no LLM)",
        "4. **assemble** → полный JSON без LLM",
        "",
        "## Per-case snapshot",
        "",
        "| id | mono label/urg/human | multi label/urg/human |",
        "|----|----------------------|------------------------|",
    ]
    mono_by = {r["id"]: r for r in mono["results"]}
    multi_by = {r["id"]: r for r in multi["results"]}
    for cid in mono_by:
        mr = mono_by[cid].get("result") or {}
        ur = multi_by[cid].get("result") or {}
        lines.append(
            f"| {cid} | {mr.get('label')}/{mr.get('urgency')}/{mr.get('needs_human')} "
            f"| {ur.get('label')}/{ur.get('urgency')}/{ur.get('needs_human')} |"
        )
    lines += ["", "Raw: `monolithic_results.json`, `multistage_results.json`.", ""]
    out = DIR / "COMPARISON.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
