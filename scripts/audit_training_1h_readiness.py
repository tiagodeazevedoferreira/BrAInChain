"""Read-only audit of the real Firebase dataset for the 1h target."""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from brainchain.firebase_reader import FirebaseReader
from brainchain.training_labels_1h import build_1h_labels
from brainchain.baseline_1h import evaluate_baseline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    reader = FirebaseReader(
        database_url=os.environ["FIREBASE_DATABASE_URL"],
        credentials_json=os.environ["FIREBASE_CREDENTIALS_JSON"],
    )
    rows = reader.read_snapshots()
    if args.max_assets:
        assets = sorted({str(r.get("source_id")) for r in rows})[: args.max_assets]
        rows = [r for r in rows if str(r.get("source_id")) in assets]

    labels = build_1h_labels(rows)
    values = [r["target_1h_label"] for r in labels]
    counts = {label: values.count(label) for label in ("down", "neutral", "up")}
    report = {
        "snapshots": len(rows),
        "eligible_1h": len(labels),
        "labels": counts,
        "baseline": evaluate_baseline(values) if values else None,
        "assets_with_labels": len({str(r["source_id"]) for r in labels}),
    }
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
