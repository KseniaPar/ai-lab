"""Run both Day 9 variants and write COMPARISON.md."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent


def run(script: str) -> None:
    print(f"\n=== {script} ===", flush=True)
    repo = DIR.parents[1]  # ai-lab
    subprocess.run(
        [sys.executable, "-u", str(DIR / script)],
        check=True,
        cwd=str(repo),
    )


def main() -> None:
    run("run_monolithic.py")
    run("run_multistage.py")
    subprocess.run(
        [sys.executable, "-u", str(DIR / "rebuild_comparison.py")],
        check=True,
        cwd=str(DIR.parents[1]),
    )


if __name__ == "__main__":
    main()
