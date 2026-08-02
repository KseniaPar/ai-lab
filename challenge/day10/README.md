# Day 10 — Micro-model first

Классификация тикетов: большинство простых кейсов закрывает **micro** без большой LLM.

| Уровень | Что |
|---------|-----|
| 1 Micro | `nomic-embed-text` + kNN по day6 `train.jsonl` → `label`, `confidence`, `OK\|UNSURE` |
| 2 Fallback | `qwen2.5-coder:7b` только если UNSURE / низкий score / битый формат |

## Запуск

```powershell
# один раз — построить индекс эмбеддингов
python -u challenge/day10/build_index.py

# прогон 28 кейсов
python -u challenge/day10/run_pipeline.py
Get-Content challenge\day10\METRICS.md
```

## Видео

1. Схема: micro → (OK? accept : LLM)
2. `METRICS.md`: % на micro vs fallback, число вызовов большой LLM, latency
3. Пример simple на micro vs hard в fallback
