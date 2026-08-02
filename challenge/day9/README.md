# Day 9 — Multi-stage inference

Задача, плохо решаемая одним запросом: из тикета сразу
`label` + `urgency` + `needs_human` + `reason`.

## Варианты

| | A Monolithic | B Multi-stage |
|-|--------------|---------------|
| Запросы | 1 большой | normalize → classify → decide → assemble |
| Модели | `qwen2.5-coder:7b` | norm `1.5b` → classify `7b` → decide **rules** |
| Формат этапов | полный JSON | compact enum JSON / rules |

## Запуск

```powershell
python -u challenge/day9/run_compare.py
Get-Content challenge\day9\COMPARISON.md
```

Или по отдельности:
```powershell
python -u challenge/day9/run_monolithic.py
python -u challenge/day9/run_multistage.py
```

## Видео

1. Показать сложный gold в `cases.jsonl` (несколько полей)
2. Схему multi-stage в README / COMPARISON
3. Таблицу accuracy / latency / LLM calls: mono vs multi
