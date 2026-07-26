# Day 3 — UNIFIED report

Generated after Level 1 (Maven) + Level 2 (browser MCP smoke).

## Level 1 — Code tests

| Status | Details |
|--------|---------|
| **PASS** | `Tests run: 22, Failures: 0, Errors: 0` |

New modules (4 classes, ≥3 required):

- `JwtServiceTest`
- `AuthServiceTest`
- `CourseOutlineServiceTest`
- `ApiExceptionHandlerTest`

Full write-up: [`level1/REPORT.md`](level1/REPORT.md)

CI: `.github/workflows/day3-ci.yml` runs `mvn test` on push/PR.

## Level 2 — UI smoke (browser MCP)

| Status | Details |
|--------|---------|
| **PASS** | S1–S5 all passed |

Driver: **cursor-ide-browser** (Playwright MCP unavailable).  
Scenarios: [`../smoke/SCENARIOS.md`](../smoke/SCENARIOS.md)  
Per-scenario log + screenshots: [`level2/REPORT.md`](level2/REPORT.md)

## Product fixes discovered by smoke

- Added **Удалить** on `frontend/courses.html` (API existed; UI did not).

## PR / deploy flow

See [`../FLOW.md`](../FLOW.md) and agent `.cursor/agents/qa-runner.md`.

Prompt after deploy:

> Я задеплоил новую фичу. Обнови smoke-сценарии и прогони Level 1 + Level 2, обнови UNIFIED.md.

## Overall

**Day 3 cycle: GREEN** (unit suite + five UI smokes with screenshots).
