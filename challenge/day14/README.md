# Day 14 — Security Step в Execution Loop («На Глазок»)

Замкнутый цикл: **генерация КБЖУ → валидация ккал → Security Step → commit**, все LLM-вызовы через Gateway `http://127.0.0.1:8000`.

## Файлы

| Файл | Роль |
|------|------|
| [`../../na-glazok/execution_loop.py`](../../na-glazok/execution_loop.py) | Цикл 4 фаз |
| [`../../na-glazok/security_prompt.py`](../../na-glazok/security_prompt.py) | Промпт инспектора |
| `run_cases.py` | 3 провокации |
| `progress.txt` | Логи прогона |
| `results.json` | Машиночитаемый итог |
| `DAY14_REPORT.md` | Сдача |

## Запуск

```powershell
# терминал 1 — шлюз (лимит выше для loop)
$env:GATEWAY_RATE_LIMIT = "40"
$env:PYTHONIOENCODING = "utf-8"
python -u na-glazok/gateway.py

# терминал 2 — тесты
$env:PYTHONIOENCODING = "utf-8"
python -u challenge/day14/run_cases.py
```
