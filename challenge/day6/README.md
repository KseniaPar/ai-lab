# Day 6 — Dataset (ticket classification)

Задача: классификация тикетов поддержки → `billing | bug | feature | access | other`.

Локальная база вместо OpenAI: **Ollama** `qwen2.5-coder:7b` (UPD: FT API недоступен).

## Артефакты

| Что | Путь |
|-----|------|
| Raw / train / eval JSONL | `dataset/*.jsonl` |
| Валидация | `validate.py` |
| Сборка + split | `build_dataset.py` |
| Baseline ×10 | `baseline/` + `run_baseline.py` |
| Критерии | `CRITERIA.md` |
| FT-клиент (dry-run) | `finetune_client.py` |

## Видео (2–4 мин)

```bash
# 1) валидация
python challenge/day6/validate.py

# 2) baseline summary
type challenge\day6\baseline\SUMMARY.md

# 3) FT-клиент без запуска job
python challenge/day6/finetune_client.py
```

## Пересборка (опционально)

```bash
python challenge/day6/build_dataset.py
# + доп. примеры через Ollama:
python challenge/day6/build_dataset.py --generate 10
python challenge/day6/run_baseline.py
```

≥20% строк — «реальные» обращения (`REAL_TICKETS` в `build_dataset.py`), остальное — шаблонный synth (+ опционально Ollama).
