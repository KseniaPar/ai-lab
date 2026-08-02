#!/usr/bin/env python3
"""Day 4 local LLM bench — same prompts, multiple Ollama models."""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path(__file__).resolve().parent / "runs"
RUNS.mkdir(parents=True, exist_ok=True)
SYS = (Path(__file__).resolve().parent / "LOCAL_SYSTEM_PROMPT.md").read_text(encoding="utf-8")

FEATURE = """Добавь GET /api/courses/{courseId}/source-summary в backend Knowbase.
Контракт JSON:
- course: { id, title, subject }
- sources: [{ id, title, sourceType, status }]
- audioCount, materialCount, readyCount
Только backend; requireOwned; dedicated *Service (не раздувать CourseService); CourseAiController.
Выдай полный код новых/изменённых Java-файлов."""

BUGFIX = """Баг: CitationTimestampTest ожидает "1:05" для 65000ms, но AskService.formatTimestamp печатает "1:5".
Найди причину, предложи минимальный фикс.
Формат ответа: Cause / Fix / Verification / Blast radius."""

MODELS = [
    ("qwen2.5-coder:7b", 8192),
    ("qwen2.5:14b", 8192),
    ("deepseek-coder:6.7b", 4096),
]


def chat(model: str, user: str, num_ctx: int) -> tuple[str, float, dict]:
    body = {
        "model": model,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_ctx": num_ctx,
            "num_predict": 1800,
        },
        "messages": [
            {"role": "system", "content": SYS},
            {"role": "user", "content": user},
        ],
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=600) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    dt = time.perf_counter() - t0
    content = payload.get("message", {}).get("content", "")
    return content, dt, payload


def run_one(model: str, task: str, prompt: str, num_ctx: int) -> None:
    slug = model.replace(":", "-").replace(".", "")
    out = RUNS / f"{task}-{slug}.md"
    print(f"==> {task} / {model}")
    try:
        content, dt, meta = chat(model, prompt, num_ctx)
        text = (
            f"# {task} — {model}\n"
            f"seconds: {dt:.1f}\n"
            f"eval_count: {meta.get('eval_count')}\n"
            f"prompt_eval_count: {meta.get('prompt_eval_count')}\n\n"
            f"---\n\n{content}\n"
        )
        out.write_text(text, encoding="utf-8")
        print(f"OK {dt:.1f}s chars={len(content)} -> {out.name}")
    except Exception as e:
        out.write_text(f"FAIL: {e}\n", encoding="utf-8")
        print(f"FAIL {e}")


def main() -> None:
    import sys
    models = MODELS
    if len(sys.argv) > 1:
        wanted = set(sys.argv[1:])
        models = [(m, c) for m, c in MODELS if m in wanted]
    for model, ctx in models:
        run_one(model, "feature", FEATURE, ctx)
        run_one(model, "bugfix", BUGFIX, ctx)


if __name__ == "__main__":
    main()
