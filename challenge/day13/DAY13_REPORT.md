# Day 13 Report — LLM Gateway («На Глазок»)

Защитный прокси OpenAI-compatible `/v1/chat/completions` с Input/Output Guard, rate limit и cost tracking.

## Чек-лист ТЗ

| Этап | Требование | Статус |
|------|------------|--------|
| 1 | FastAPI proxy + JSON-аудит (`audit.jsonl`) + `[AUDIT]` лог | DONE |
| 2 | Input Guard: secrets → 400; PII → redact | DONE |
| 3 | Output Guard: prompt leak, API keys, `protein.ru` | DONE |
| 4 | Rate limit 5/min/IP; cost gpt-4o-mini $0.15/$0.60 per 1M | DONE |
| 5 | 10 автотестов | **10/10 PASS** |

## Результаты тестов

| # | Кейс | Ожидание | Результат |
|---|------|----------|-----------|
| 1 | AWS `AKIA…` | HTTP 400 | PASS |
| 2 | Карта | `[REDACTED_CARD]` + ответ | PASS |
| 3 | Email | `[REDACTED_EMAIL]` | PASS |
| 4 | Base64 `c2st…` | HTTP 400 | PASS |
| 5 | `sk-` + `proj-…` (склейка) | HTTP 400 | PASS |
| 6 | Телефон | `[REDACTED_PHONE]` | PASS |
| 7 | Чистый промпт | 200 + cost log | PASS |
| 8 | 6 запросов подряд | 6-й → 429 | PASS |
| 9 | `protein.ru` в ответе | Output Guard | PASS |
| 10 | Слив «нутрициолог бота» | Output Guard | PASS |

Запуск: `python -u challenge/day13/test_gateway.py`  
Лог: [`progress.txt`](progress.txt), JSON: [`audit.jsonl`](audit.jsonl).

Тесты идут через FastAPI `TestClient` + mock `call_upstream` (без сети). Live-режим: `python challenge/day13/gateway.py` → OpenRouter.

## Выдержки `[AUDIT]`

```
[AUDIT] - ЗАБЛОКИРОВАНО: Обнаружен критический секрет AWS_KEY от IP testclient
[AUDIT] - ЗАБЛОКИРОВАНО: Обнаружен Base64-encoded секрет от IP testclient
[AUDIT] - ЗАБЛОКИРОВАНО: Обнаружен критический секрет OPENAI_KEY от IP testclient
[AUDIT] - Запрос успешно завершен. Токены: Вход=11, Выход=22 | Стоимость: $0.000015
[AUDIT] - IP testclient превысил лимит запросов!
[AUDIT] - КРИТИЧЕСКИЙ СБОЙ: Подозрительная фишинговая ссылка (protein.ru) в ответе!
[AUDIT] - КРИТИЧЕСКИЙ СБОЙ: Попытка слива System Prompt в ответе модели!
```

## Cost Tracking (пример из audit.jsonl)

- Чистый промпт (блины): `in_tokens=11`, `out_tokens=22`, `cost_usd ≈ $0.000015`
- Тариф: `$0.15 / 1M` input, `$0.60 / 1M` output (`PRICE_*_1K = 0.00015 / 0.00060`)

## Замечания реализации

- Upstream: OpenRouter `https://openrouter.ai/api/v1/chat/completions` (в образце ТЗ URL был некорректный `https://openai.com`).
- Паттерн OpenAI-ключа: `sk-[a-zA-Z0-9\-]{20,}` — с дефисами, иначе `sk-proj-…` не ловится.
- Ключ: `OPENROUTER_API_KEY` / `REAL_OPENAI_API_KEY` / `application-local.yml`.
- `GATEWAY_MOCK=1` — тесты без реального ключа.
