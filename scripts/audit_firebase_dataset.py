"""Run a read-only aggregate audit against Firebase snapshot history."""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from brainchain.firebase_training_data import build_training_rows
from brainchain.dataset_audit import audit_rows
from brainchain.firebase_reader import FirebaseReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    reader = FirebaseReader(
        database_url=os.environ["FIREBASE_DATABASE_URL"],
        credentials_json=os.environ["FIREBASE_CREDENTIALS_JSON"],
    )
    raw = reader.read_snapshots()
    rows = build_training_rows(raw)
    if args.max_assets:
        assets = sorted({str(r.get("source_id")) for r in rows})[: args.max_assets]
        rows = [r for r in rows if str(r.get("source_id")) in assets]
    report = audit_rows(rows)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
