# Day 5 — Metrics

## Task pools

| Pool | Tracker | Count |
|------|---------|-------|
| Run 1 | `tasks/backlog.json` | **18** (T01–T18) |
| Run 2 (stretch, after rule tweaks) | `tasks/backlog-run2.json` | **8** (R01–R08) |

## Run 1 (cloud Cursor agents)

| Metric | Value |
|--------|-------|
| Completed consecutively without user intervention | **18 / 18** |
| First-shot success rate | **100%** |
| Where it broke | **Did not break** |
| Sum of per-task verify times (LOG) | **138 s (~2.3 min)** |
| **Wall time without pause** (first task commit → last) | **11.1 minutes** |
| Avg wall per task | **~0.6 min** |

Log: [`run1/LOG.md`](run1/LOG.md)

## Rule tweaks before Run 2

Updated `.cursor/rules/java-backend.mdc` with Day5 loop lessons:
- already-satisfied tasks → note + PASS
- never invent `com.ailab.knowbase` / DTO/JPA layers
- one commit per backlog task; stop streak on first FAIL

## Run 2 (cloud, harder stretch)

| Metric | Value |
|--------|-------|
| Completed consecutively | **8 / 8** |
| First-shot success rate | **100%** |
| Where it broke | **Did not break** |
| Sum verify times | **43 s** |
| **Wall time without pause** | **3.5 minutes** |
| Avg wall per task | **~0.4 min** |

Log: [`run2/LOG.md`](run2/LOG.md)

### Run1 vs Run2

| | Run 1 | Run 2 |
|--|-------|-------|
| Streak | 18 | 8 (smaller harder pool; still unbroken) |
| Pause-free minutes | **11.1** | **3.5** |
| Combined cloud pause-free | **14.6 minutes** across both streaks |

Run 2 did not “die later” — with tightened rules it also finished clean. The meaningful comparison vs Day4 local hallucinations: cloud respects `com.ailab.*` and verifies with Maven.

## Local model (Ollama `qwen2.5-coder:7b`)

Sample of same-pool tasks T01 / T06 / T16 (generate-only, no tools):

| Task | Result | Seconds |
|------|--------|---------|
| T01 | REVIEW-OK | 68 |
| T06 | **FAIL** (missing ownership/route in output) | 128 |
| T16 | REVIEW-OK | 89 |

| Metric | Local |
|--------|-------|
| Tasks actually implemented + committed in a loop | **0** |
| Plausible sketches / 3 | **2 / 3** |
| Consecutive execution-loop streak | **0** (no agent tools) |
| Pause-free minutes of real delivery | **0** |

Log: [`local/LOG.md`](local/LOG.md)

## Cloud vs local (execution loop)

| | Cloud agents | Local Qwen2.5-Coder 7B |
|--|--------------|-------------------------|
| Can take tracker → code → test → commit | **Yes** | No (chat only) |
| Max consecutive delivered tasks | **18** then **8** | **0** delivered |
| Pause-free delivery time | **11.1 + 3.5 = 14.6 min** | n/a |
| Style fidelity | High with project rules | Often invents packages (Day4/Day5) |

## Bottom line

- **Cloud execution loop:** full 18-task pool without pause (**11.1 min** wall), then 8 stretch tasks (**3.5 min**) after rule polish — **0 failures**.
- **Local model:** useful for sketches; **cannot sustain Day5 loop**; **0** end-to-end tasks without a human/cloud agent applying patches.
