# Day 11 — «На Глазок» (Prompt Injection)

Telegram-бот расчёта КБЖУ + лабораторные атаки по ТЗ дня 11.

**Сдача:** [`DAY11_REPORT.md`](DAY11_REPORT.md)

| Файл | Назначение |
|------|------------|
| [`calorie_core.py`](calorie_core.py) | Baseline / hardened + `[USER_INPUT]` |
| [`SYSTEM_PROMPTS.md`](SYSTEM_PROMPTS.md) | Тексты промптов |
| [`run_attacks.py`](run_attacks.py) | 3 атаки ТЗ × 2 режима |
| [`ATTACK_LOG.md`](ATTACK_LOG.md) | Логи |
| [`attacks/`](attacks/) | Транскрипты (= скриншоты) |
| [`INJECTION_COLLECTION.md`](INJECTION_COLLECTION.md) | 5 инъекций |
| [`bot.py`](bot.py) | Telegram (aiogram) |

## Запуск атак

```powershell
cd C:\Users\user\Projects\ai-lab
python -u challenge/day11/run_attacks.py
```

## Бот

```powershell
# TELEGRAM_BOT_TOKEN или telegram-local.txt
python -u challenge/day11/bot.py
```
