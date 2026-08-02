
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "challenge"))
# load run_confidence as a module by path
import importlib.util
spec = importlib.util.spec_from_file_location(
    "run_confidence", Path(__file__).resolve().parent / "run_confidence.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

case = json.loads(sys.argv[1])
redundancy = int(sys.argv[2])
model = sys.argv[3]
try:
    out = mod.run_pipeline(case["text"], model=model, redundancy_n=redundancy)
except Exception as exc:
    out = {
        "decision": "REJECT",
        "label": None,
        "final": None,
        "reason": f"pipeline_error:{type(exc).__name__}",
        "llm_calls": 0,
        "retries": 0,
        "latency_sec": 0.0,
        "trace": [{"step": "error", "error": str(exc)}],
    }
gold = case.get("gold")
row = {
    "id": case["id"],
    "kind": case["kind"],
    "gold": gold,
    "label_match_gold": (gold is None or out.get("label") == gold) if gold is not None else None,
    **{k: out[k] for k in ("decision", "label", "reason", "llm_calls", "retries", "latency_sec", "final")},
    "trace": out["trace"],
}
print(json.dumps(row, ensure_ascii=False))
