# Day 8 — Routing between models

Та же задача: классификация тикетов.
Сначала дешёвая/быстрая модель, при неуверенности — более сильная.

| Роль | Модель |
|------|--------|
| small / fast | `qwen2.5-coder:1.5b` |
| strong / fallback | `qwen2.5:14b` |

## Эвристика `should_escalate`

Эскалация, если:
- сломан JSON / label не из enum / короткий reason
- нет или низкий `confidence` (< 0.7)
- два вызова small дали разные label
- второй вызов small невалиден / reason слишком короткий

## Артефакты

| Что | Путь |
|-----|------|
| Кейсы (≥15) | `cases.jsonl` |
| Роутер | `run_routing.py` |
| Отчёт | `ROUTING_REPORT.md` |
| Сырые результаты | `results.json` |

## Видео

```powershell
python -u challenge/day8/run_routing.py
Get-Content challenge\day8\ROUTING_REPORT.md
```

Показать таблицу: какие запросы остались на 1.5b, какие ушли на 14b.
