"""Validate day6 JSONL: valid JSON, roles, non-empty content, label enum."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LABELS = {"billing", "bug", "feature", "access", "other"}
REQUIRED_ROLES = ("system", "user", "assistant")


def validate_line(line: str, line_no: int) -> list[str]:
    errors: list[str] = []
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as exc:
        return [f"L{line_no}: invalid JSON ({exc})"]

    if not isinstance(obj, dict):
        return [f"L{line_no}: root must be object"]

    messages = obj.get("messages")
    if not isinstance(messages, list):
        return [f"L{line_no}: missing messages array"]
    if len(messages) != 3:
        errors.append(f"L{line_no}: expected 3 messages, got {len(messages)}")

    roles = []
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            errors.append(f"L{line_no}: messages[{i}] not object")
            continue
        role = msg.get("role")
        content = msg.get("content")
        roles.append(role)
        if role not in REQUIRED_ROLES:
            errors.append(f"L{line_no}: messages[{i}] bad role={role!r}")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"L{line_no}: messages[{i}] empty content")

    if roles[:3] != list(REQUIRED_ROLES) and len(roles) >= 3:
        errors.append(f"L{line_no}: roles must be system,user,assistant got {roles}")

    if len(messages) >= 3 and isinstance(messages[2], dict):
        raw = messages[2].get("content") or ""
        try:
            gold = json.loads(raw)
            if gold.get("label") not in LABELS:
                errors.append(f"L{line_no}: assistant.label not in enum: {gold.get('label')!r}")
            if not str(gold.get("reason") or "").strip():
                errors.append(f"L{line_no}: assistant.reason empty")
        except json.JSONDecodeError:
            errors.append(f"L{line_no}: assistant content is not JSON")

    return errors


def validate_file(path: Path) -> int:
    if not path.is_file():
        print(f"FAIL: file not found: {path}", file=sys.stderr)
        return 1
    errors: list[str] = []
    n = 0
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                errors.append(f"L{line_no}: empty line")
                continue
            n += 1
            errors.extend(validate_line(line, line_no))

    if errors:
        print(f"FAIL {path}: {len(errors)} issue(s), {n} rows")
        for e in errors[:40]:
            print(f"  {e}")
        if len(errors) > 40:
            print(f"  … +{len(errors) - 40} more")
        return 1

    print(f"OK {path}: {n} rows")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="JSONL files (default: dataset/raw train eval)",
    )
    args = ap.parse_args()
    base = Path(__file__).resolve().parent / "dataset"
    files = args.files or [base / "raw.jsonl", base / "train.jsonl", base / "eval.jsonl"]
    code = 0
    for path in files:
        code |= validate_file(path)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
