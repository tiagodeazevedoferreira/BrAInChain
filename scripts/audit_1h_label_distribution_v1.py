from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta

from brainchain.firebase_reader import FirebaseReader


def parse_ts(value: object) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    by_asset: dict[str, list[dict]] = {}
    for row in rows:
        source = row.get("source_id")
        captured = parse_ts(row.get("captured_at"))
        if source is None or captured is None:
            continue
        item = dict(row)
        item["_ts"] = captured
        by_asset.setdefault(str(source), []).append(item)

    labels = Counter()
    eligible = 0
    for asset_rows in by_asset.values():
        asset_rows.sort(key=lambda r: r["_ts"])
        for i, row in enumerate(asset_rows):
            current = row.get("price")
            if current in (None, 0):
                continue
            target = row["_ts"] + timedelta(hours=1)
            future = None
            for candidate in asset_rows[i + 1 :]:
                if candidate["_ts"] <= target:
                    future = candidate
                    continue
                break
            if future is None:
                continue
            elapsed = future["_ts"] - row["_ts"]
            # Avoid treating nearly adjacent snapshots as a 1h label.
            if elapsed < timedelta(minutes=45):
                continue
            future_price = future.get("price")
            if future_price in (None, 0):
                continue
            eligible += 1
            multiplier = float(future_price) / float(current)
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
