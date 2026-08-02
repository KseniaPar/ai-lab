# Day 8 — Routing report

- Small: `qwen2.5-coder:1.5b` → Strong: `qwen2.5:14b`
- Confidence threshold: **0.7**
- Cases: **16**
- Stayed on small: **10** (62%)
- Escalated to strong: **6** (38%)
- LLM calls: **38** · avg latency **6.59s**/case

## Heuristic `should_escalate`

Escalate if any of:
- invalid JSON / label not in enum / empty reason / missing confidence
- `confidence` < 0.7
- two small calls disagree on label
- second small call invalid while first ok
- reason too short

Otherwise stay on small (**if unsure → escalate**).

## By kind

| kind | n | small | strong |
|------|---|-------|--------|
| borderline | 4 | 3 | 1 |
| easy | 7 | 4 | 3 |
| mixed | 2 | 1 | 1 |
| noisy | 3 | 2 | 1 |

## Per request

| id | kind | route | label | escalate_reason | s |
|----|------|-------|-------|-----------------|---|
| R01 | easy | **strong** | billing | `redundancy_disagreement:billing/bug` | 12.891 |
| R02 | easy | **small** | bug | `confident_on_small` | 3.824 |
| R03 | easy | **small** | feature | `confident_on_small` | 3.268 |
| R04 | easy | **strong** | access | `redundancy_disagreement:bug/billing` | 11.834 |
| R05 | easy | **strong** | billing | `redundancy_disagreement:billing/bug|strong_failed` | 12.425 |
| R06 | easy | **small** | billing | `confident_on_small` | 4.417 |
| R07 | borderline | **small** | billing | `confident_on_small` | 3.198 |
| R08 | borderline | **small** | bug | `confident_on_small` | 4.203 |
| R09 | borderline | **strong** | bug | `redundancy_disagreement:billing/bug` | 12.938 |
| R10 | borderline | **small** | billing | `confident_on_small` | 3.685 |
| R11 | noisy | **small** | bug | `confident_on_small` | 2.775 |
| R12 | noisy | **small** | bug | `confident_on_small` | 2.427 |
| R13 | noisy | **strong** | other | `redundancy_disagreement:billing/other` | 9.943 |
| R14 | mixed | **strong** | billing | `redundancy_disagreement:bug/billing` | 11.537 |
| R15 | mixed | **small** | bug | `confident_on_small` | 2.865 |
| R16 | easy | **small** | billing | `confident_on_small` | 3.153 |

Raw: `results.json`. Cases: `cases.jsonl`.
