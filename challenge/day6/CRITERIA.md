# Критерии оценки (после fine-tune / routing в следующих днях)

Точка отсчёта: ответы базовой модели `qwen2.5-coder:7b` на 10 примерах из `dataset/eval.jsonl`
(см. `baseline/SUMMARY.md` и `baseline/baseline_responses.jsonl`).

«Стало лучше», если на том же eval-срезе:

1. **Точность label** — доля точных совпадений `pred_label == gold_label` выше baseline.
2. **Формат** — доля ответов, где парсится JSON с `label ∈ {billing,bug,feature,access,other}` и непустым `reason`, ≥ baseline (цель: 100%).
3. **Стиль reason** — одно короткое предложение на русском, без markdown/оговорок («как ИИ…»), без смены языка.

Не считаем улучшением: более длинные ответы, «уверенный» тон без верного label, частичные совпадения категорий.
