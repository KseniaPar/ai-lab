# Day 2 — Profile iterations

## First-shot results

| Profile | Task | First run | Agent |
|---------|------|-----------|-------|
| Bug Fix | `CitationTimestampTest` (`1:5` vs `1:05`) | ✅ fixed + tests green | [bug-fix run](4d60b4dc-55fb-4a66-82a1-a7efffaf550b) |
| Research | Как устроена авторизация | ✅ structured answer, no code edits | [research run](a0261a94-0978-469a-88e8-4a55e576276c) |
| Feature Builder | `GET .../conspect/export` Markdown download | ✅ compile OK + README + thin UI | [feature-builder run](9eb114c3-a974-4fea-bf7e-ad1d973699c5) |

Logs: `challenge/day2/runs/*/RESULT.md`

## What we still tightened after success

Even though all three worked on the first attempt, profiles were refined from observed edge cases:

1. **Research** — allow only `challenge/**/runs/**/RESULT.md` writes when the parent asks for an artifact; keep all product code read-only.
2. **Bug Fix** — explicitly forbid weakening assertions; call out citation/UI label formatting in blast-radius checks.
3. **Feature Builder** — document that non-JSON downloads may use `fetch` + Bearer instead of JSON `api()`.

No second verification runs were required (criteria already met on attempt 1).
