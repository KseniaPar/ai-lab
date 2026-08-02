# Baseline — qwen2.5-coder:7b

- Samples: **10** (from `dataset/eval.jsonl`)
- Exact label match: **6/10** (60%)
- Valid JSON label in enum: **10/10**
- Mean latency: **4.77s**

| # | gold | pred | match | s |
|---|------|------|-------|---|
| 1 | bug | bug | Y | 12.472 |
| 2 | bug | bug | Y | 4.143 |
| 3 | other | access | N | 3.236 |
| 4 | other | billing | N | 4.788 |
| 5 | billing | billing | Y | 3.691 |
| 6 | billing | billing | Y | 3.547 |
| 7 | other | billing | N | 2.704 |
| 8 | other | access | N | 2.862 |
| 9 | feature | feature | Y | 6.01 |
| 10 | billing | billing | Y | 4.294 |

Raw responses: `baseline_responses.jsonl`. Criteria: `CRITERIA.md`.
