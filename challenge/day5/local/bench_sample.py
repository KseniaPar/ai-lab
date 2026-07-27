#!/usr/bin/env python3
import json, time, urllib.request
from pathlib import Path

sysp = Path("challenge/day4/LOCAL_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
tasks = [
    ("T01", "Implement GET /api/health for Knowbase Spring Boot: 200 {status:ok} without auth. SecurityConfig permitAll. Package com.ailab.*. Full Java."),
    ("T06", "Implement GET /api/courses/{courseId}/source-summary with course, sources[], audioCount, materialCount, readyCount. Dedicated service, requireOwned, CourseAiController. Use existing com.ailab packages only — never com.ailab.knowbase."),
    ("T16", "Implement in-memory ask rate limit per user N/minute. IllegalStateException with Russian message. Config app.ask.rate-limit-per-minute. com.ailab.qa package."),
]
out = Path("challenge/day5/local")
out.mkdir(parents=True, exist_ok=True)
lines = [
    "# Day 5 — Local model attempt\n\n",
    "Model: `qwen2.5-coder:7b` · temp=0.2 · **no tools / no compile**\n\n",
    "| Task | Result | Seconds | Why |\n|------|--------|---------|-----|\n",
]

for tid, prompt in tasks:
    body = {
        "model": "qwen2.5-coder:7b",
        "stream": False,
        "options": {"temperature": 0.2, "top_p": 0.9, "num_ctx": 4096, "num_predict": 1200},
        "messages": [
            {"role": "system", "content": sysp},
            {"role": "user", "content": prompt},
        ],
    }
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            content = json.loads(r.read().decode())["message"]["content"]
        dt = time.perf_counter() - t0
        (out / f"{tid}.md").write_text(content, encoding="utf-8")
        ok = False
        why = ""
        if "com.ailab.knowbase" in content:
            ok, why = False, "invented com.ailab.knowbase"
        elif tid == "T01":
            ok = "/api/health" in content or "HealthController" in content
            why = "health sketch present" if ok else "missing health endpoint"
        elif tid == "T06":
            ok = "requireOwned" in content and "source-summary" in content and "com.ailab." in content
            why = "ownership+route ok" if ok else "missing ownership or route"
        else:
            ok = "rate" in content.lower() and (
                "IllegalStateException" in content or "rate-limit" in content
            )
            why = "rate-limit sketch" if ok else "incomplete rate limit"
        result = "REVIEW-OK" if ok else "FAIL"
        lines.append(f"| {tid} | {result} | {dt:.0f} | {why} |\n")
        print(tid, result, f"{dt:.0f}s", why)
    except Exception as e:
        lines.append(f"| {tid} | FAIL | - | {e} |\n")
        print(tid, "ERR", e)

lines.append(
    "\nREVIEW-OK = plausible text only; **0 tasks applied/committed by local model** "
    "(cannot run execution loop with tools).\n"
)
(out / "LOG.md").write_text("".join(lines), encoding="utf-8")
