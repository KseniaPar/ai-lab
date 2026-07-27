---
name: execution-loop
description: >-
  Knowbase Day 5 execution loop. Use when processing tasks/backlog.json
  autonomously: pick next todo task, choose profile, implement, verify, commit, log.
model: inherit
readonly: false
---

# Execution Loop — Knowbase

You process `tasks/backlog.json` one task at a time without asking the user.

## MUST do

1. Read backlog; pick the first task with status missing/`todo` (or next id after last DONE in the run log).
2. Choose profile from task.profile: `bug-fix` / `research` / `feature-builder` (read `.cursor/agents/<profile>.md`).
3. Implement only that task until `done_when` is met.
4. Verify: compile and/or targeted `mvn test` as required by `done_when`.
5. Commit with message `day5: <id> <short title>` (author via env if needed). Do not push unless the run instructions say so.
6. Append a row to the run LOG: id, profile, result PASS/FAIL, seconds, notes.
7. On FAIL: stop the streak, write failure reason, do not continue to next task in the same streak.

## MUST NOT do

- Skip verification
- Expand scope beyond `done_when`
- Ask clarifying questions
- Commit secrets
- Mark PASS if `done_when` unmet
