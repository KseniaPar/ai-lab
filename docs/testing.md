# Knowbase testing

Day 3 defined two verification levels for this repo. Prefer them over ad-hoc checks when validating changes.

## Level 1 — `mvn test`

Run unit and focused service tests from `backend/`:

```bash
mvn -q test
```

Or a single class, e.g. `mvn -q -Dtest=CourseServiceTest test`.

Coverage lives under `backend/src/test/java/com/ailab/...`. Day 3 Level 1 write-up: [challenge/day3/reports/level1/REPORT.md](../challenge/day3/reports/level1/REPORT.md). Overview of the day: [challenge/day3/README.md](../challenge/day3/README.md).

## Level 2 — UI smoke

Manual / agent-driven smoke against the running UI (`5173`) and API (`8081`), following scenarios in [challenge/day3/smoke/SCENARIOS.md](../challenge/day3/smoke/SCENARIOS.md). Day 3 Level 2 report: [challenge/day3/reports/level2/REPORT.md](../challenge/day3/reports/level2/REPORT.md). End-to-end PR cycle notes: [challenge/day3/FLOW.md](../challenge/day3/FLOW.md).
