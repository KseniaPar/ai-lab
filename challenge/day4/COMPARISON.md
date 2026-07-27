# Day 4 — Cloud vs Local comparison (Knowbase)

## Setup under test

| Side | Stack |
|------|--------|
| Cloud | Cursor Agent (Composer / cloud models) + project `.cursor/rules` — Days 1–2 |
| Local | **Ollama 0.31.2** + **Continue.dev** in Cursor · system prompt = Day 1 rules (`LOCAL_SYSTEM_PROMPT.md`) · `temp=0.2`, `top_p=0.9`, `num_ctx=4–8k` |

Hardware: Ryzen 7 8845HS, ~31 GB RAM, Radeon 780M iGPU.

## Same tasks

1. **Feature (Day 1 style):** `GET /api/courses/{id}/source-summary` (dedicated service, ownership, contract).
2. **Agent bugfix (Day 2 style):** citation `1:5` → `1:05` (`formatTimestamp`).

Raw local outputs: `challenge/day4/runs/`.

## Local model bake-off

| Model | Feature time | Bugfix time | Feature quality (vs Knowbase style) | Bugfix quality | First-shot usable? |
|-------|--------------|---------------|--------------------------------------|-----------------|--------------------|
| **qwen2.5-coder:7b** | **115 s** | **34 s** | Mentions `requireOwned` + dedicated service, but invents packages (`com.ailab.knowbase.*`), field `@Autowired`, wrong ID types | Correct **`%02d`** fix; vague root-cause wording | Bugfix **yes**; feature **needs rewrite** |
| **qwen2.5:14b** | **438 s** | **66 s** | Longer answer, still wrong layout (`com.ailab.service/dto`), `@Autowired`, weak ownership wiring | Correct `%02d`; invents public static API | Bugfix **yes**; feature **no** (too slow + style miss) |
| **deepseek-coder:6.7b** | **142 s** | **49 s** | Partial contract; invents `Source` entities; `requireOwned` misplaced on controller | **Wrong diagnosis** (rounding) though snippet has `%02d` | Bugfix **no**; feature **no** |

### Best local combo on this machine

**Chat/edit:** `qwen2.5-coder:7b` · **temp 0.2** · **top_p 0.9** · **ctx 8192**  
**Autocomplete:** `qwen2.5-coder:1.5b` · **temp 0.1** · **maxPromptTokens 1024**  
**Embed / codebase:** `nomic-embed-text`  
**Rules:** Continue `rules:` = Day 1 condensed prompt  

14B is not worth the ~4× latency here without better package fidelity. DeepSeek 6.7B lost the bugfix task.

## Cloud vs best local

| Criterion | Cloud Cursor Agent | Local (Qwen2.5-Coder 7B + Continue) |
|-----------|--------------------|--------------------------------------|
| Code quality (project fit) | **High** — correct packages, constructor injection, compiles on first agent pass (Day 1 outline / Day 2 timestamp) | **Medium** — right high-level idea, wrong scaffolding without open files |
| Speed | Fast for agent loops (seconds–low minutes wall with tools) | Feature ~2 min, bugfix ~30 s pure generation; no tools unless you paste context |
| Project context | Reads repo via tools; rules + skills + agents | Rules in system prompt + Continue codebase/embed; still hallucinated non-existent packages |
| Offline | Needs network | **Works offline** once models pulled |
| Autocomplete | Cursor Tab (cloud) | Local FIM via Continue + `qwen2.5-coder:1.5b` |
| Multi-file agent loop | Native (search, edit, test, iterate) | Weak unless you manually feed files / use Continue edit carefully |

## When local is enough

- Tab autocomplete / small completions in open file  
- Explaining a pasted snippet  
- Drafting a **single-method** fix when the bug is stated precisely (e.g. `%02d`)  
- Offline travel / privacy-sensitive drafts  
- Brainstorming API shapes before cloud agent implements  

## When cloud is hard to replace

- Multi-file features that must match **existing** package layout  
- Agent loops: find → fix → `mvn test` → iterate  
- Smoke / browser / CI orchestration (Day 3)  
- Large refactors and ownership/security edge cases  
- When first-shot compile + style conformance matters  

## Verdict

Local **Ollama + Continue + Qwen2.5-Coder 7B/1.5B** is a solid **offline co-pilot** for Knowbase, especially autocomplete and narrow bugfixes. For Day 1/2 class agent work, **cloud Cursor remains the primary**; use local as a second opinion or offline backup — after pasting real files from `com.ailab.*`.
