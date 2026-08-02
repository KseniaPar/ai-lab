# Setup checklist — Continue + Ollama for Knowbase

1. Ollama running (tray) — models:
   ```
   ollama list
   # expect: qwen2.5-coder:7b, qwen2.5-coder:1.5b, qwen2.5:14b, deepseek-coder:6.7b, nomic-embed-text
   ```
2. Continue extension installed in Cursor (`Continue.continue` v2+) — **Reload Window**.
3. Open this repo so workspace `.continue/config.yaml` loads (also copied to `%USERPROFILE%\.continue\config.yaml`).
4. Continue sidebar → model **Qwen2.5-Coder 7B (chat)**; autocomplete uses **1.5B**.
5. Optional: run `python challenge/day4/bench_local.py` to refresh local vs local bake-off.
