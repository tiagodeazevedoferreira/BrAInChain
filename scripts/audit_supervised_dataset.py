"""Audit the real Firebase-derived supervised dataset without training a model."""
from __future__ import annotations

import argparse
import json

from brainchain.dataset_builder import build_dataset, training_counts
from brainchain.firebase_reader import FirebaseReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    if args.max_assets > 0:
        allowed = set()
        for row in rows:
            asset = str(row.get("source_id") or row.get("symbol") or row.get("id") or "")
            if asset:
                allowed.add(asset)
        allowed = set(sorted(allowed)[: args.max_assets])
        rows = [row for row in rows if str(row.get("source_id") or row.get("symbol") or row.get("id") or "") in allowed]

    dataset = build_dataset(rows)
    summary = {
        "snapshot_rows": len(rows),
        "supervised_rows": len(dataset),
        "training_counts": training_counts(dataset),
        "feature_complete_rows": sum(
            all(row.get(key) is not None for key in (
                "price_usd", "market_cap_usd", "volume_24h_usd", "percent_change_24h"
            ))
            for row in dataset
        ),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
