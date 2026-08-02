# Day 9 — Monolithic vs Multi-stage

Задача: из одного тикета извлечь **несколько полей** — `label`, `urgency`, `needs_human`, `reason` (плохо одним запросом).

## Variants

| | Monolithic (A) | Multi-stage (B) |
|-|----------------|-----------------|
| Models | `qwen2.5-coder:7b` x1 | norm `qwen2.5-coder:1.5b` + clf `qwen2.5-coder:7b` + decide **rules** |
| LLM calls / case | 1 | 2 (+0 rules) |
| Cases | 10 | 10 |
| Valid JSON | 60% | 80% |
| label acc | 50% | 50% |
| urgency acc | 90% | 70% |
| needs_human acc | 100% | 80% |
| all fields | 50% | 40% |
| LLM calls total | 10 | 20 |
| Latency total | 59.28s | 28.1s |
| Latency avg | 5.93s | 2.81s |

## Multi-stage pipeline

1. **normalize** → `{"clean":"..."}` (1.5b, short)
2. **classify** → `{"label":"enum"}` (7b, short)
3. **decide** → `{"urgency":"low|medium|high","needs_human":bool}` (rules, no LLM)
4. **assemble** → полный JSON без LLM

## Per-case snapshot

| id | mono label/urg/human | multi label/urg/human |
|----|----------------------|------------------------|
| M01 | billing/high/True | billing/high/True |
| M02 | bug/medium/False | bug/medium/False |
| M03 | feature/low/False | feature/low/False |
| M04 | access/high/True | access/high/True |
| M05 | billing|other/low/False | None/None/None |
| M06 | billing|bug/high/True | access/high/True |
| M07 | billing|bug/low/False | bug/medium/False |
| M08 | access/low/False | None/None/None |
| M09 | access|bug/high/True | bug/high/True |
| M10 | bug/low/False | bug/medium/False |

Raw: `monolithic_results.json`, `multistage_results.json`.
