# Day 10 — Micro-model first metrics

- Micro: **nomic-embed-text** kNN over day6 train (`index.json`)
- Big LLM fallback: `qwen2.5-coder:7b`
- Cases: **28**
- Handled by micro only: **25** (89%)
- Went to LLM fallback: **3** (11%)
- Big LLM calls total: **3**
- Latency avg: **0.54s**/case (total 15.01s)

## By kind

| kind | n | micro | fallback | label acc |
|------|---|-------|----------|-----------|
| simple | 12 | 10 | 2 | 75% |
| borderline | 8 | 8 | 0 | 50% |
| hard | 8 | 7 | 1 | 67% |

## Gate to fallback

- micro status `UNSURE`
- best cosine sim < 0.72 or label-margin < 0.03
- confidence < 0.55 or invalid label

Raw: `results.json`. Cases: `cases.jsonl`.
