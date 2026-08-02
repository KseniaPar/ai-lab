"""Shared helpers for Day 9 monolithic / multi-stage inference."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LABELS = ("billing", "bug", "feature", "access", "other")
URGENCY = ("low", "medium", "high")

DIR = Path(__file__).resolve().parent


def strip_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    return text.strip()


def parse_json_obj(text: str) -> dict[str, Any] | None:
    text = strip_fence(text)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None


def load_cases(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or (DIR / "cases.jsonl")
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def validate_result(obj: dict[str, Any] | None) -> tuple[bool, list[str]]:
    errs: list[str] = []
    if obj is None:
        return False, ["not_json"]
    if obj.get("label") not in LABELS:
        errs.append("bad_label")
    if obj.get("urgency") not in URGENCY:
        errs.append("bad_urgency")
    if not isinstance(obj.get("needs_human"), bool):
        errs.append("bad_needs_human")
    if not str(obj.get("reason") or "").strip():
        errs.append("empty_reason")
    return len(errs) == 0, errs


def field_score(pred: dict[str, Any] | None, gold: dict[str, Any]) -> dict[str, bool]:
    if not pred:
        return {k: False for k in ("label", "urgency", "needs_human")}
    return {
        "label": pred.get("label") == gold.get("label"),
        "urgency": pred.get("urgency") == gold.get("urgency"),
        "needs_human": pred.get("needs_human") == gold.get("needs_human"),
    }


def decide_urgency_rules(clean_text: str, label: str) -> dict[str, Any]:
    """Cheap deterministic stage-3: urgency + needs_human from keywords + label."""
    t = clean_text.lower()
    high_kw = (
        "срочн", "asap", "сегодня", "суд", "утечк", "риск", "эскалац",
        "не может войти", "половина команды", "urgent", "blocker",
    )
    med_kw = ("падает", "зависа", "не проходит", "слома", "ошибк", "не примен")
    human_kw = ("суд", "утечк", "enterprise", "эскалац", "asap", "риск", "команды")

    urgency = "low"
    if any(k in t for k in high_kw):
        urgency = "high"
    elif any(k in t for k in med_kw):
        urgency = "medium"
    elif label in ("bug", "access", "billing"):
        urgency = "medium"

    needs_human = any(k in t for k in human_kw) or urgency == "high"
    if label == "feature" and urgency == "low":
        needs_human = False
    if label == "other" and urgency == "low":
        needs_human = False

    return {"urgency": urgency, "needs_human": needs_human}
