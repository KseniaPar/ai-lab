# Day 2 — Profiles (Knowbase)

Custom Cursor subagents live in `.cursor/agents/` (see [Subagents](https://cursor.com/docs/subagents.md)).

| Profile | File | Role |
|---------|------|------|
| Bug Fix | `bug-fix.md` | Find cause → minimal fix → verify tests |
| Research | `research.md` | Read-only architecture answers (`readonly: true`) |
| Feature Builder | `feature-builder.md` | Small vertical slice (third profile) |

## Verification tasks

| Profile | Task | Log |
|---------|------|-----|
| Bug Fix | Failing `CitationTimestampTest` / citation `mm:ss` padding | `runs/bug-fix/` |
| Research | How auth works (JWT filter → controllers) | `runs/research/` |
| Feature Builder | Export latest conspect as downloadable Markdown | `runs/feature-builder/` |

## Iteration notes

See `ITERATIONS.md` for first-shot results and post-success profile tweaks.
Artifact logs: `runs/bug-fix/RESULT.md`, `runs/research/RESULT.md`, `runs/feature-builder/RESULT.md`.
