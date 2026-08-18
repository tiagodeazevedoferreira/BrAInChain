from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta

from brainchain.firebase_reader import FirebaseReader

THRESHOLDS = (0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02)


def _time(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-assets", type=int, default=0)
    args = parser.parse_args()

    rows = FirebaseReader().read_snapshots()
    groups: dict[str, list[dict]] = {}
    for row in rows:
        if row.get("source_id") is None or row.get("price_usd") is None or row.get("captured_at") is None:
            continue
        item = dict(row)
        item["_time"] = _time(row["captured_at"])
        item["_price"] = float(row["price_usd"])
        groups.setdefault(str(row["source_id"]), []).append(item)

    returns: list[float] = []
    for asset_rows in groups.values():
        asset_rows.sort(key=lambda r: r["_time"])
        for i, current in enumerate(asset_rows):
            end = current["_time"] + timedelta(hours=1)
            future = [r for r in asset_rows[i + 1 :] if r["_time"] <= end]
            if not future:
                continue
            if future[-1]["_time"] - current["_time"] < timedelta(minutes=45):
                continue
            returns.append(future[-1]["_price"] / current["_price"] - 1.0)

    results = {}
    for threshold in THRESHOLDS:
        counts = Counter()
        for value in returns:
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
