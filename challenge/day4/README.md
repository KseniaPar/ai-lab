# Day 4 — Local Boost (Knowbase)

## Hardware

| Item | Value |
|------|--------|
| CPU | AMD Ryzen 7 8845HS (8c/16t) |
| RAM | ~31 GB |
| GPU | AMD Radeon 780M (iGPU, shared memory) |
| Runtime | Ollama **0.31.2** |

## IDE stack

- **Continue.dev** `Continue.continue` v2.0.0 installed in **Cursor** (and VS Code if present)
- Config: project `.continue/config.yaml` + synced `~/.continue/config.yaml`
- System prompt / rules: `LOCAL_SYSTEM_PROMPT.md` (Day 1 rules condensed) → Continue `rules:` block
- Chat models: `qwen2.5-coder:7b` (default), `qwen2.5:14b`, `deepseek-coder:6.7b`
- Autocomplete: `qwen2.5-coder:1.5b` (FIM-friendly, low latency)
- Embeddings: `nomic-embed-text` (codebase context)
- Generation: **temperature 0.15–0.2**, **top_p 0.9**, chat **contextLength 4–8k**, autocomplete **maxPromptTokens 1024**

## How to use in Cursor

1. Ensure Ollama is running (`ollama serve` / tray app).
2. Reload Cursor window after Continue install.
3. Open Continue sidebar → pick **Qwen2.5-Coder 7B (chat)**.
4. Tab autocomplete uses **Qwen2.5-Coder 1.5B**.
5. Optional slash prompts: `knowbase-feature`, `knowbase-bugfix`.

## Bench

```powershell
python challenge/day4/bench_local.py
```

Results: `challenge/day4/runs/` · Comparison: `COMPARISON.md`
