# Day 3 — Dev / PR testing flow

## After opening a PR (or before merge)

1. **Level 1 — code tests**
   ```powershell
   cd backend
   & "..\..\llm-chat-app\.tools\apache-maven-3.9.6\bin\mvn.cmd" -q test
   ```
   Or: `gh workflow run` / push triggers `.github/workflows/day3-ci.yml`.

2. **Level 2 — UI smoke** (servers must be up)
   ```powershell
   # terminal A
   cd backend; mvn -q spring-boot:run
   # terminal B
   cd frontend; npm run dev
   ```
   Then invoke the **qa-runner** agent: “Прогони smoke SCENARIOS.md через browser MCP и обнови reports/level2”.

3. **Unified report**
   Agent writes `challenge/day3/reports/UNIFIED.md` combining Level 1 + Level 2.

## Scenario: “я задеплоил новую фичу”

Prompt for **qa-runner**:

> Я задеплоил новую фичу. Обнови `challenge/day3/smoke/SCENARIOS.md` под изменения (новые кнопки/роуты), затем прогони Level 1 (`mvn test`) и Level 2 (browser MCP), сохрани скриншоты и единый отчёт `reports/UNIFIED.md`. Если что упало — укажи вероятное место в коде.

## CI

GitHub Actions job `day3-ci` runs Maven tests on push/PR to `day3` / `master`. Smoke stays agent+MCP (needs live UI).
