# Day 1 — Rules (Knowbase)

## Config layers used

| Layer | Where | Role |
|-------|--------|------|
| Global | Cursor **User Rules** (Settings → Rules) | Language, commit hygiene, general prefs — must not override project stack |
| Local | `.cursor/rules/*.mdc`, `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md` | Stack, architecture, examples, antipatterns |
| Skill | `.cursor/skills/add-course-endpoint/SKILL.md` | Checklist for course-scoped APIs |
| Subagents | Cursor Task (isolated implementer) | One-shot battle prompt, no back-and-forth |

## Battle prompt (fixed for v1 and v2)

See `BATTLE_PROMPT.md` — same text both runs.

## Artifacts

- `rules-v1-snapshot/` — rules before iteration
- `generation-v1/` — first assistant output (diff + notes)
- `generation-v2/` — second assistant output after rules v2
- `COMPARISON.md` — diff analysis + what improved quality most

Final code on branch `day1` is the **v2** generation (kept).
