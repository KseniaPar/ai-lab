# Day 7 — Confidence metrics

- Model: `qwen2.5-coder:7b`
- Cases: **14**
- ACCEPT: **7** · REJECT: **7** (reject rate 50%)
- Cases with retry (constraint re-infer): **0** (retries total 0)
- LLM calls: **45** total · avg **3.21**/case
- Latency: **271.76s** total · avg **19.41s**/case
- Cost proxy: number of LLM calls (local Ollama, $0 cloud)

## By kind

| kind | n | ACCEPT | REJECT |
|------|---|--------|--------|
| correct | 5 | 4 | 1 |
| borderline | 4 | 3 | 1 |
| noisy | 5 | 0 | 5 |

## Approaches used

1. **Constraint-based** — input signal + JSON parse, label ∈ enum, reason length
2. **Redundancy** — independent classify calls, majority ≥2
3. **Self-check** — second model pass OK / FIX / UNSURE

Raw: `results.json`. Cases: `cases.jsonl`.
