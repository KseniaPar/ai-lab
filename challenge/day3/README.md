# Day 3 — Testing (Knowbase)

Two levels:

| Level | What | Where |
|-------|------|--------|
| 1 — Code | Unit/integration tests on business logic | `backend/src/test/...` + `reports/level1/` |
| 2 — UI smoke | Agent drives UI via **cursor-ide-browser MCP** (Playwright MCP not installed in this workspace) | `smoke/SCENARIOS.md` + `reports/level2/` |

## Full cycle / PR flow

See `FLOW.md` and `.github/workflows/day3-ci.yml`.

Agent profile for re-runs: `.cursor/agents/qa-runner.md`.
