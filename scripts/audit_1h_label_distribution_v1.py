from __future__ import annotations

import argparse
import json
from collections import Counter

from brainchain.firebase_reader import FirebaseReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    by_asset: dict[str, list[dict]] = {}
    for row in rows:
        source = row.get("source_id")
        captured = row.get("captured_at")
        if source is None or captured is None:
            continue
        by_asset.setdefault(str(source), []).append(row)

    labels = Counter()
    eligible = 0
    for asset_rows in by_asset.values():
        asset_rows.sort(key=lambda r: str(r.get("captured_at")))
        for i, row in enumerate(asset_rows):
            if i + 1 >= len(asset_rows):
                continue
            current = row.get("price")
            if current in (None, 0):
                continue
            # Use the first later observation as the currently available 1h label proxy.
            future = asset_rows[i + 1].get("price")
            if future is None:
                continue
            eligible += 1
            multiplier = float(future) / float(current)
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
