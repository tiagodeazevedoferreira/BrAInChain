from __future__ import annotations

import argparse
import json
from collections import Counter

from brainchain.firebase_reader import FirebaseReader
from brainchain.label_engine import build_time_labels

THRESHOLDS = (0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    if args.max_assets:
        rows = rows[: args.max_assets]

    labeled = build_time_labels(rows, horizons_hours=(1,))
    results = {}
    for threshold in THRESHOLDS:
        counts = Counter()
        for row in labeled:
            value = row.get("return_1h")
            if value is None:
                continue
            value = float(value)
            if value >= threshold:
                counts["up"] += 1
            elif value <= -threshold:
                counts["down"] += 1
            else:
                counts["neutral"] += 1
        total = sum(counts.values())
        results[f"{threshold:.4f}"] = {
            "eligible": total,
            "up": counts["up"],
            "down": counts["down"],
            "neutral": counts["neutral"],
            "min_class": min(counts.values()) if total else 0,
        }

    print(json.dumps(results, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
