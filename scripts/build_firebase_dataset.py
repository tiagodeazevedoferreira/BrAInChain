"""Build a training-ready JSON dataset from Firebase snapshots."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from brainchain.firebase_reader import FirebaseReader
from brainchain.firebase_training_data import build_training_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/firebase_training_rows.json")
    args = parser.parse_args()

    reader = FirebaseReader()
    snapshots = reader.read("/snapshots") or {}
    rows = build_training_rows(snapshots)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"snapshots_read={len(snapshots) if isinstance(snapshots, dict) else 0}")
    print(f"training_rows={len(rows)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
