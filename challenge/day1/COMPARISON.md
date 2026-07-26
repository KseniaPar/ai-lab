# Day 1 — Comparison: generation v1 vs v2

Same battle prompt: `BATTLE_PROMPT.md` (`GET /api/courses/{courseId}/outline`).  
Agents: [Battle v1](c7f300c3-6f19-4a87-9d95-a1ae49aa1e08) → [Battle v2](6a58278a-e597-47a0-9a38-da8a00e10bec).

## Scorecard

| Criterion | v1 (rules v1) | v2 (rules v2) |
|-----------|---------------|---------------|
| Compiles (`mvn -DskipTests compile`) | ✅ | ✅ |
| Contract fields match | ✅ | ✅ |
| `requireOwned` | ✅ | ✅ |
| `SecurityException` → 403 | ✅ | ✅ |
| Dedicated aggregate service | ❌ logic in `CourseService` | ✅ `CourseOutlineService` |
| No dual SQL (JdbcTemplate + Repository) | ❌ new `ConspectRepository`, `ConspectService` still on JdbcTemplate | ✅ `ConspectService` migrated to repo |
| Existence check style | `COUNT(*) > 0` | `SELECT 1 … LIMIT 1` |
| README API table | ❌ | ✅ |
| `CourseService` stays CRUD-only | ❌ | ✅ |
| Linter / style fit | mostly OK | better package boundaries |

## Structural diff (high level)

```text
v1: CourseAiController → CourseService.outline()
         + LectureRepository / ChunkRepository / ConspectRepository injected into CourseService
         + ConspectRepository only for exists; ConspectService still uses JdbcTemplate

v2: CourseAiController → CourseOutlineService.outline()
         + CourseService untouched (ownership/CRUD)
         + ConspectRepository shared; ConspectService fully on repository
         + README row for GET /outline
```

See also:
- `generation-v1/full.diff` + `generation-v1/files/`
- `generation-v2/full.diff` + `generation-v2/files/`
- `rules-v1-snapshot/` vs current `.cursor/rules` / skill

## What rules v1 missed (fixed in v2)

1. Explicit ban on bloating `CourseService` with aggregates  
2. Mandatory dedicated `*Service` for course aggregates  
3. Ban on dual access paths when introducing a feature repository  
4. Prefer EXISTS / limit-1 for booleans  
5. Hard requirement: README API row for public routes  
6. Domain note: materials = `lectures.source_type = MATERIAL`  
7. `SecurityException`→403 called out in always-on / Java rules (not only skill checklist)

## What most improved quality

1. **«CourseService = CRUD only»** — biggest structural win (clean layering)  
2. **«No dual JdbcTemplate + Repository»** — forced Conspect refactor, consistent persistence  
3. **Skill checklist + examples** — both runs already hit ownership, camelCase, compile  
4. **README duty** — documentation hygiene only appeared after v2  
5. **Global + local + skill + subagent** — local/skill drove code shape; subagent kept one-shot battle fair; global snippet set precedence

## Screenshots / artifacts

GitHub/file diffs are the primary evidence (this challenge folder). Open:
- `generation-v1/full.diff`
- `generation-v2/full.diff`

Optional: PR diff on branch `day1` vs `master` after push.
