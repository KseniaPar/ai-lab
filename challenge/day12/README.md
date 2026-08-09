# Day 12 — Indirect Prompt Injection («На Глазок»)

Слой обработки **внешних данных**: рецепт/состав/«страница» с скрытыми инструкциями → baseline vs 3 защитных слоя.

Одна модель для обоих режимов: `openai/gpt-4o-mini` (чистота эксперимента).

## Файлы

| Файл | Роль |
|------|------|
| `fixtures/*.txt` | 3 вектора + кейс Bard/Docs |
| `defenses.py` | sanitize / XML `<user_data>` / output validation |
| `calorie_core.py` | `reply_external(mode=baseline\|defended)` |
| `run_attacks.py` | прогон 4×2, логи |
| `ATTACK_LOG.md` | человекочитаемый лог |
| `DAY12_REPORT.md` | чек-лист сдачи |

## Запуск

```powershell
python -u challenge/day12/run_attacks.py
```

Ключ: `OPENROUTER_API_KEY` или `application-local.yml` (как day11).
Модель: `OPENROUTER_MODEL` (дефолт `openai/gpt-4o-mini`).
