# Day 11 — «На Глазок» (Prompt Injection)

Telegram-бот расчёта КБЖУ + лабораторные атаки по ТЗ дня 11.

**Сдача:** [`DAY11_REPORT.md`](DAY11_REPORT.md)

**Актуальный runtime (бот + LLM Gateway)** перенесён в модуль [`na-glazok/`](../../na-glazok/). Запуск:

```powershell
python -u na-glazok/gateway.py   # терминал 1
python -u na-glazok/bot.py       # терминал 2
```

См. [`na-glazok/README.md`](../../na-glazok/README.md).

## Артефакты day11 (челлендж)

| Файл | Назначение |
|------|------------|
| [`calorie_core.py`](calorie_core.py) | Baseline / hardened + `[USER_INPUT]` (снимок day11) |
| [`SYSTEM_PROMPTS.md`](SYSTEM_PROMPTS.md) | Тексты промптов |
| [`run_attacks.py`](run_attacks.py) | 3 атаки ТЗ × 2 режима |
| [`ATTACK_LOG.md`](ATTACK_LOG.md) | Логи |
| [`attacks/`](attacks/) | Транскрипты |
| [`INJECTION_COLLECTION.md`](INJECTION_COLLECTION.md) | 5 инъекций |
| [`bot.py`](bot.py) | Снимок Telegram-бота day11 |

## Запуск атак (лаборатория day11)

```powershell
python -u challenge/day11/run_attacks.py
```
