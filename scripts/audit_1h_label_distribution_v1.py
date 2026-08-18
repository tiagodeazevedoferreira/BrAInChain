from __future__ import annotations

import argparse
import json
from collections import Counter

from brainchain.firebase_reader import FirebaseReader
from brainchain.labels import build_time_labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    if args.max_assets > 0:
        rows = rows[: args.max_assets]

    # Reuse the production label builder so this audit uses the same
    # price field (price_usd, with price as fallback) and temporal semantics
    # as the supervised-label pipeline.
    labeled = build_time_labels(rows, horizons_hours=(1,))

    labels = Counter()
    eligible = 0
    for row in labeled:
        value = row.get("label_1h_max_return")
        if value is None:
            continue
        eligible += 1
        multiplier = 1.0 + float(value)
        if multiplier >= 1.02:
            labels["up_2pct"] += 1
        elif multiplier <= 0.98:
            labels["down_2pct"] += 1
        else:
            labels["neutral"] += 1

    print(json.dumps({"eligible": eligible, "labels": dict(labels)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
