"""Day 10 — build embedding index from day6 train.jsonl (nomic-embed-text)."""
from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[1]  # ai-lab
TRAIN = ROOT / "challenge" / "day6" / "dataset" / "train.jsonl"
OUT = DIR / "index.json"
EMBED_MODEL = "nomic-embed-text"
HOST = "http://127.0.0.1:11434"


def embed(text: str, model: str = EMBED_MODEL) -> list[float]:
    body = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{HOST}/api/embeddings",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    vec = payload.get("embedding")
    if not vec:
        # newer /api/embed
        body2 = json.dumps({"model": model, "input": text}).encode("utf-8")
        req2 = urllib.request.Request(
            f"{HOST}/api/embed",
            data=body2,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req2, timeout=120) as resp2:
            payload2 = json.loads(resp2.read().decode("utf-8"))
        embs = payload2.get("embeddings") or []
        vec = embs[0] if embs else None
    if not vec:
        raise RuntimeError(f"no embedding in response: {payload}")
    return [float(x) for x in vec]


def l2_normalize(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", type=Path, default=TRAIN)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--model", default=EMBED_MODEL)
    args = ap.parse_args()

    rows = []
    with args.train.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            ex = json.loads(line)
            user = next(m["content"] for m in ex["messages"] if m["role"] == "user")
            gold = json.loads(next(m["content"] for m in ex["messages"] if m["role"] == "assistant"))
            rows.append({"text": user, "label": gold["label"]})

    print(f"embedding {len(rows)} train examples with {args.model}...", flush=True)
    items = []
    for i, row in enumerate(rows, 1):
        vec = l2_normalize(embed(row["text"], args.model))
        items.append({"text": row["text"], "label": row["label"], "vector": vec})
        if i % 10 == 0 or i == len(rows):
            print(f"  {i}/{len(rows)}", flush=True)

    payload = {"model": args.model, "items": items}
    args.out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {args.out} ({len(items)} vectors)", flush=True)


if __name__ == "__main__":
    main()
