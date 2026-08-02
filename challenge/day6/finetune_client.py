"""Local fine-tune client (Ollama Modelfile) — prepare + dry-run by default.

OpenAI Fine-tuning API недоступен (блокировка). Аналог пайплайна:
  1) upload/prepare training file
  2) create fine-tune job (ollama create from Modelfile)
  3) poll until model visible

Do NOT run a real create unless --execute is passed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

DIR = Path(__file__).resolve().parent
DEFAULT_TRAIN = DIR / "dataset" / "train.jsonl"
DEFAULT_OUT = DIR / "ft_prepare"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def prepare(train_path: Path, out_dir: Path, base_model: str) -> Path:
    """Convert JSONL chat examples into a Modelfile + training messages dump."""
    out_dir.mkdir(parents=True, exist_ok=True)
    examples = []
    with train_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    # Ollama native create does not do full SFT like OpenAI FT;
    # we package messages for a future adapter / document the upload step,
    # and build a Modelfile that bakes SYSTEM + few-shot MESSAGE pairs
    # (demo-ready substitute when cloud FT is blocked).
    messages_path = out_dir / "training_messages.jsonl"
    with messages_path.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    system = examples[0]["messages"][0]["content"]
    # Few-shot bake-in (first 8) — keeps Modelfile small for demo
    shots = examples[:8]
    lines = [
        f"FROM {base_model}",
        f'SYSTEM """{system}"""',
        "PARAMETER temperature 0.1",
        "PARAMETER num_predict 128",
    ]
    for ex in shots:
        user = ex["messages"][1]["content"].replace('"""', '"')
        asst = ex["messages"][2]["content"].replace('"""', '"')
        lines.append(f'MESSAGE user """{user}"""')
        lines.append(f'MESSAGE assistant """{asst}"""')

    modelfile = out_dir / "Modelfile"
    modelfile.write_text("\n".join(lines) + "\n", encoding="utf-8")

    meta = {
        "step": "upload/prepare",
        "train_path": str(train_path),
        "examples": len(examples),
        "messages_file": str(messages_path),
        "modelfile": str(modelfile),
        "base_model": base_model,
        "note": "Full weight FT via OpenAI unavailable; Modelfile few-shot create is local stand-in.",
    }
    (out_dir / "upload_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return modelfile


def create_job(modelfile: Path, model_name: str, dry_run: bool) -> dict:
    cmd = ["ollama", "create", model_name, "-f", str(modelfile)]
    if dry_run:
        print("[dry-run] would run:", " ".join(cmd))
        return {"status": "dry_run", "command": cmd, "model": model_name}
    proc = run(cmd, check=False)
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"create failed: {proc.returncode}")
    return {"status": "created", "model": model_name}


def poll_status(model_name: str, timeout_sec: int = 120, interval: float = 2.0) -> dict:
    """Poll until `ollama show` succeeds or timeout."""
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        proc = run(["ollama", "show", model_name], check=False)
        if proc.returncode == 0:
            return {"status": "succeeded", "model": model_name, "detail": proc.stdout[:500]}
        print(f"  polling… ({model_name} not ready)")
        time.sleep(interval)
    return {"status": "timeout", "model": model_name}


def main() -> None:
    ap = argparse.ArgumentParser(description="Fine-tune client (Ollama local stand-in)")
    ap.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--base-model", default="qwen2.5-coder:7b")
    ap.add_argument("--model-name", default="knowbase-ticket-clf")
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Actually run `ollama create` (default: dry-run only)",
    )
    ap.add_argument("--poll", action="store_true", help="After create, poll ollama show")
    args = ap.parse_args()

    print("=== 1) upload / prepare ===")
    modelfile = prepare(args.train, args.out, args.base_model)

    dry = not args.execute
    print("=== 2) create fine-tune job ===")
    job = create_job(modelfile, args.model_name, dry_run=dry)
    print(json.dumps(job, ensure_ascii=False, indent=2))

    if args.poll and not dry:
        print("=== 3) poll status ===")
        status = poll_status(args.model_name)
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif dry:
        print("=== 3) poll status ===")
        print("[dry-run] would poll: ollama show", args.model_name)

    print("Done. Use --execute to run create for real (not required for Day 6).")


if __name__ == "__main__":
    main()
