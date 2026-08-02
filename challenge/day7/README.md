# Day 7 — Confidence & quality gate

Задача та же, что Day 6: классификация тикетов (`billing|bug|feature|access|other`).
Без fine-tune: инференс с оценкой уверенности и контролем принятия результата.

## Подходы

1. **Constraint-based** — сигнал входа (шум/пусто) + JSON, enum, длина `reason`
2. **Redundancy** — 2 независимых вызова, majority (оба должны совпасть)
3. **Self-check** — второй проход: `OK` / `FIX` / `UNSURE`

Решение: `ACCEPT` | `REJECT` (+ retry classify при сломанных constraints).

## Артефакты

| Что | Путь |
|-----|------|
| Кейсы (correct / borderline / noisy) | `cases.jsonl` |
| Пайплайн | `run_confidence.py` |
| Стабильный прогон (1 кейс = 1 процесс) | `run_all_cases.py` |
| Результаты | `results.json` |
| Метрики | `METRICS.md` |

## Видео

```powershell
python challenge/day7/run_all_cases.py
Get-Content challenge\day7\METRICS.md
```

Ожидаемо: **correct** чаще ACCEPT, **noisy** — REJECT; смотреть reject rate, LLM calls, latency.
