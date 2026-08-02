"""Day 6 — support-ticket classification dataset builder.

Creates ≥50 JSONL examples (system+user+assistant), cleans, splits train/eval.
Optional: --generate N calls Ollama to invent more user texts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))

from common.ollama_client import chat  # noqa: E402

DIR = Path(__file__).resolve().parent
DATASET = DIR / "dataset"
LABELS = ("billing", "bug", "feature", "access", "other")

SYSTEM = (
    "Ты классификатор тикетов поддержки. "
    "Ответь ТОЛЬКО валидным JSON без markdown: "
    '{"label":"<enum>","reason":"<одно короткое предложение>"}. '
    "label ∈ billing|bug|feature|access|other."
)

# ≥20% «реальных»: короткие тексты в стиле живых обращений в поддержку SaaS.
REAL_TICKETS: list[tuple[str, str, str]] = [
    (
        "billing",
        "Добрый день! С карты списали 2990 ₽ дважды за одну подписку Pro за март. Чек прикладываю, верните лишнее.",
        "Двойное списание за подписку — типичный billing.",
    ),
    (
        "billing",
        "Нужен акт сверки и счёт-фактура за Q1 на ООО «Альфа», ИНН 7701234567. Отправьте на accounting@alpha.ru.",
        "Запрос закрывающих документов — billing.",
    ),
    (
        "billing",
        "Хочу отменить автопродление. В личном кабинете кнопки нет, подписка спишется 5-го.",
        "Отмена автопродления относится к биллингу.",
    ),
    (
        "bug",
        "После обновления iOS приложение падает при открытии раздела «Курсы». Версия 3.12.1, iPhone 14, лог во вложении.",
        "Крах приложения — дефект (bug).",
    ),
    (
        "bug",
        "Экспорт PDF конспекта обрезает кириллицу: вместо букв квадратики. Chrome 131, Windows 11.",
        "Битый экспорт PDF — bug.",
    ),
    (
        "bug",
        "Кнопка «Сохранить» на странице профиля ничего не делает: сеть 200, но данные не меняются после F5.",
        "Сохранение не персистится — bug.",
    ),
    (
        "feature",
        "Можно ли добавить тёмную тему в веб-кабинет? Глаза устают вечером при разборе лекций.",
        "Запрос новой возможности — feature.",
    ),
    (
        "feature",
        "Нужен bulk-upload материалов: сейчас грузим по одному файлу, у курса 40 PDF.",
        "Массовая загрузка — запрос фичи.",
    ),
    (
        "access",
        "Не приходит письмо для сброса пароля на anna.k@example.com. Проверила «Спам», писем нет уже час.",
        "Проблема со входом/сбросом пароля — access.",
    ),
    (
        "access",
        "Коллегу уволили, отключите ему доступ к workspace «Knowbase Prod» (user id u_88421) ASAP.",
        "Отзыв доступа сотрудника — access.",
    ),
    (
        "access",
        "SSO через Google зависает на callback: белый экран после согласия. Корп. аккаунт @corp.example.",
        "Сбой SSO/логина — access.",
    ),
    (
        "other",
        "Подскажите, где в документации описан лимит минут STT на тарифе Free?",
        "Вопрос по документации/лимитам без инцидента — other.",
    ),
    (
        "other",
        "Можно ли использовать Knowbase для школьных кружков (некоммерция)? Нужна ссылка на ToS.",
        "Общий организационный вопрос — other.",
    ),
    (
        "billing",
        "Промокод STUDENT50 не применяется на checkout: пишет «истёк», хотя на сайте ещё висит баннер.",
        "Проблема с промокодом/оплатой — billing.",
    ),
    (
        "bug",
        "Таймкоды в цитатах Q&A сдвинуты на ~30 секунд относительно аудиоплеера.",
        "Неверные таймкоды — bug.",
    ),
]

# Синтетические шаблоны (остальные ≥80% датасета).
SYNTH: list[tuple[str, list[str], str]] = [
    (
        "billing",
        [
            "Не проходит оплата картой Visa *4412, ошибка 3DS. Тариф Team.",
            "Верните деньги за неиспользованные 2 месяца подписки Business.",
            "Смените плательщика на другой юр. адрес, договор тот же.",
            "Пришла квитанция на английском — нужна русская версия для бухгалтерии.",
            "Upgrade с Free на Pro прошёл, но в кабинете всё ещё Free.",
            "Хочу перейти на годовую оплату со скидкой, как это сделать?",
            "Invoice #INV-20441 оплачен, статус в кабинете всё ещё Unpaid.",
            "Нужна расшифровка строки «AI usage overage $18.40» в счёте.",
        ],
        "Вопрос про оплату, счёт или подписку — billing.",
    ),
    (
        "bug",
        [
            "Поиск по корпусу возвращает пусто, хотя лекции в статусе READY.",
            "При загрузке WAV 90 МБ прогресс зависает на 47% и не падает с ошибкой.",
            "Дублируются сообщения в чате Q&A при медленной сети.",
            "На Safari 17 ломается вёрстка страницы курса: кнопки уезжают вправо.",
            "STT иногда теряет последние 2–3 минуты длинной лекции.",
            "Уведомления email приходят дважды на одно событие «conspect ready».",
            "Фильтр по дате в списке лекций игнорирует часовой пояс пользователя.",
            "После удаления материала chunk'и остаются в выдаче поиска.",
        ],
        "Некорректное поведение продукта — bug.",
    ),
    (
        "feature",
        [
            "Хотим webhook на событие «conspect.ready» для нашей CRM.",
            "Добавьте экспорт конспекта в Notion одним кликом.",
            "Нужны роли viewer/editor внутри курса, не только owner.",
            "Просьба: офлайн-режим мобильного приложения для чтения конспектов.",
            "Интеграция с Zoom: автозагрузка записи вебинара в курс.",
            "Хотелось бы шаблоны промптов Q&A на уровне workspace.",
            "Сделайте сортировку материалов drag-and-drop.",
            "API для программного создания курса из нашего LMS.",
        ],
        "Запрос новой функциональности — feature.",
    ),
    (
        "access",
        [
            "Заблокировали аккаунт после 5 неудачных логинов, разблокируйте please.",
            "Нужен доступ read-only к курсу «Оргхимия-2026» для стажёра.",
            "2FA приложение потерял — восстановите через backup codes не выходит.",
            "Приглашение в workspace истекло, пришлите новое на same email.",
            "Не могу принять invite: «email mismatch» хотя почта верная.",
            "Отключите API-ключ sk_live_… — возможно утёк в лог.",
            "Передайте ownership курса с u_12 на u_99, я ухожу в отпуск.",
            "IP allowlist режет мой домашний IP, добавьте 85.12.x.x.",
        ],
        "Проблема с доступом, правами или аутентификацией — access.",
    ),
    (
        "other",
        [
            "Какой SLA у тарифа Enterprise на ответы support?",
            "Пришлите one-pager для закупки в вузе (PDF).",
            "Работаете ли вы с персональными данными по 152-ФЗ?",
            "Где прайс на on-prem установку?",
            "Можно ли заказать обучение команды админов (1 день)?",
            "Есть ли статус-страница инцидентов?",
            "Подскажите контакт для партнёрской программы.",
            "Нужна цитата для пресс-релиза о вашей STT-модели — кто press?",
        ],
        "Общий вопрос без инцидента продукта — other.",
    ),
]


def make_example(label: str, user: str, reason: str) -> dict:
    assistant = json.dumps({"label": label, "reason": reason}, ensure_ascii=False)
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user.strip()},
            {"role": "assistant", "content": assistant},
        ]
    }


def fingerprint(ex: dict) -> str:
    user = next(m["content"] for m in ex["messages"] if m["role"] == "user")
    return hashlib.sha256(user.strip().lower().encode("utf-8")).hexdigest()


def build_seed() -> list[dict]:
    out: list[dict] = []
    for label, user, reason in REAL_TICKETS:
        out.append(make_example(label, user, reason))
    for label, texts, reason in SYNTH:
        for text in texts:
            out.append(make_example(label, text, reason))
    return out


def generate_more(n: int, model: str, existing: list[dict]) -> list[dict]:
    """Ask Ollama to invent ticket texts; we attach gold labels from the prompt."""
    seen = {fingerprint(e) for e in existing}
    added: list[dict] = []
    rounds = 0
    while len(added) < n and rounds < n * 4:
        rounds += 1
        label = LABELS[rounds % len(LABELS)]
        prompt = (
            f"Придумай один реалистичный текст обращения в поддержку SaaS (на русском, 1–3 предложения). "
            f"Категория должна однозначно быть: {label}. "
            f"Верни ТОЛЬКО текст обращения, без JSON и кавычек."
        )
        try:
            text, _, _ = chat(
                [{"role": "user", "content": prompt}],
                model=model,
                temperature=0.9,
                num_predict=120,
            )
        except RuntimeError as exc:
            print(f"generate skip: {exc}", file=sys.stderr)
            break
        text = text.strip().strip('"').strip()
        if len(text) < 20 or len(text) > 600:
            continue
        reason = {
            "billing": "Обращение про оплату/счёт — billing.",
            "bug": "Описание дефекта — bug.",
            "feature": "Запрос новой возможности — feature.",
            "access": "Проблема доступа — access.",
            "other": "Общий вопрос — other.",
        }[label]
        ex = make_example(label, text, reason)
        fp = fingerprint(ex)
        if fp in seen:
            continue
        seen.add(fp)
        added.append(ex)
        print(f"  + generated [{label}] {text[:60]}…")
    return added


def clean(examples: list[dict]) -> list[dict]:
    seen: set[str] = set()
    cleaned: list[dict] = []
    for ex in examples:
        msgs = ex.get("messages") or []
        if len(msgs) != 3:
            continue
        roles = [m.get("role") for m in msgs]
        if roles != ["system", "user", "assistant"]:
            continue
        if any(not str(m.get("content") or "").strip() for m in msgs):
            continue
        user = msgs[1]["content"].strip()
        if len(user) < 20 or len(user) > 800:
            continue
        try:
            gold = json.loads(msgs[2]["content"])
        except json.JSONDecodeError:
            continue
        if gold.get("label") not in LABELS:
            continue
        if not str(gold.get("reason") or "").strip():
            continue
        fp = fingerprint(ex)
        if fp in seen:
            continue
        seen.add(fp)
        cleaned.append(ex)
    return cleaned


def split_train_eval(examples: list[dict], seed: int = 42) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    items = list(examples)
    rng.shuffle(items)
    n_eval = max(1, round(len(items) * 0.2))
    eval_set = items[:n_eval]
    train_set = items[n_eval:]
    return train_set, eval_set


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build day6 ticket-classification dataset")
    ap.add_argument("--generate", type=int, default=0, help="Extra examples via Ollama")
    ap.add_argument("--model", default="qwen2.5-coder:7b")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    examples = build_seed()
    print(f"seed: {len(examples)} (real={len(REAL_TICKETS)}, synth templates)")
    if args.generate > 0:
        print(f"generating {args.generate} via {args.model}…")
        examples.extend(generate_more(args.generate, args.model, examples))

    cleaned = clean(examples)
    if len(cleaned) < 50:
        raise SystemExit(f"need ≥50 after clean, got {len(cleaned)}")

    write_jsonl(DATASET / "raw.jsonl", cleaned)
    train, eval_set = split_train_eval(cleaned, seed=args.seed)
    write_jsonl(DATASET / "train.jsonl", train)
    write_jsonl(DATASET / "eval.jsonl", eval_set)

    real_share = len(REAL_TICKETS) / len(cleaned)
    print(f"cleaned: {len(cleaned)}")
    print(f"real share: {real_share:.0%} ({len(REAL_TICKETS)}/{len(cleaned)})")
    print(f"train: {len(train)}  eval: {len(eval_set)}")
    print(f"wrote {DATASET / 'raw.jsonl'}")
    print(f"wrote {DATASET / 'train.jsonl'}")
    print(f"wrote {DATASET / 'eval.jsonl'}")


if __name__ == "__main__":
    main()
