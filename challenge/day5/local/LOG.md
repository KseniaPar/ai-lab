# Day 5 — Local model attempt

Model: `qwen2.5-coder:7b` · temp=0.2 · **no tools / no compile**

| Task | Result | Seconds | Why |
|------|--------|---------|-----|
| T01 | REVIEW-OK | 68 | health sketch present |
| T06 | FAIL | 128 | missing ownership or route |
| T16 | REVIEW-OK | 89 | rate-limit sketch |

REVIEW-OK = plausible text only; **0 tasks applied/committed by local model** (cannot run execution loop with tools).
