from __future__ import annotations

import argparse
import json
from collections import Counter

from brainchain.firebase_reader import FirebaseReader
from brainchain.labels import ONE_HOUR_RETURN_THRESHOLD, build_time_labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    if args.max_assets > 0:
        rows = rows[: args.max_assets]

    # Reuse the production label builder so this audit uses the same
    # price field, temporal semantics, and promoted 1h threshold as training.
    labeled = build_time_labels(rows, horizons_hours=(1,))

    labels = Counter()
    eligible = 0
    for row in labeled:
        value = row.get("label_1h_max_return")
        if value is None:
            continue
        eligible += 1
        labels[row.get("label_1h_class")] += 1

    print(json.dumps({
        "eligible": eligible,
        "threshold": ONE_HOUR_RETURN_THRESHOLD,
        "labels": dict(labels),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
