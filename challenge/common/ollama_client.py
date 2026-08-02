"""Minimal Ollama /api/chat client shared by challenge day6+ scripts."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

DEFAULT_HOST = "http://127.0.0.1:11434"


def chat(
    messages: list[dict[str, str]],
    *,
    model: str = "qwen2.5-coder:7b",
    host: str = DEFAULT_HOST,
    temperature: float = 0.2,
    num_predict: int = 256,
    num_ctx: int = 4096,
    timeout: int = 180,
) -> tuple[str, float, dict[str, Any]]:
    """Send a chat request. Returns (content, latency_sec, raw_payload)."""
    body = {
        "model": model,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
        },
        "messages": messages,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama unavailable at {host}: {exc}") from exc
    dt = time.perf_counter() - t0
    content = (payload.get("message") or {}).get("content") or ""
    return content.strip(), dt, payload
