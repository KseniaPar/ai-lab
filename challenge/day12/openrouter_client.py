"""Minimal OpenRouter chat client for challenge day12."""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_api_key() -> str:
    env = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if env:
        return env
    local = _repo_root() / "backend" / "src" / "main" / "resources" / "application-local.yml"
    if local.is_file():
        text = local.read_text(encoding="utf-8")
        m = re.search(r"api-key:\s*(\S+)", text)
        if m:
            key = m.group(1).strip().strip("'\"")
            if key and "PASTE" not in key and key != "sk-not-set":
                return key
    raise RuntimeError(
        "OpenRouter API key not found. Set OPENROUTER_API_KEY or "
        "backend/src/main/resources/application-local.yml app.openrouter.api-key"
    )


def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 512,
    timeout: int = 120,
    retries: int = 3,
) -> tuple[str, float, dict[str, Any]]:
    """Send chat completions request. Returns (content, latency_sec, raw_payload)."""
    key = api_key or load_api_key()
    model_name = model or os.environ.get("OPENROUTER_MODEL") or DEFAULT_MODEL
    body = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(body).encode("utf-8")
    url = f"{DEFAULT_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "HTTP-Referer": "https://github.com/local/ai-lab-challenge",
        "X-Title": "ai-lab-challenge-day12",
        "User-Agent": "ai-lab-day12/1.0",
    }

    t0 = time.perf_counter()
    last_err: Exception | None = None
    payload: dict[str, Any] = {}
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            last_err = None
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            last_err = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
                continue
            raise RuntimeError(f"OpenRouter unavailable after {retries} tries: {exc}") from exc
    if last_err is not None:
        raise RuntimeError(f"OpenRouter unavailable: {last_err}") from last_err

    dt = time.perf_counter() - t0
    choices = payload.get("choices") or []
    content = ""
    if choices:
        content = ((choices[0].get("message") or {}).get("content")) or ""
    return content.strip(), dt, payload
