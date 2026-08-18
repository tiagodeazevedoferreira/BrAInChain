"""Descriptive audit for the historical Firebase training dataset."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _positive_price(row: Mapping[str, Any]) -> bool:
    for key in ("price_usd", "price"):
        try:
            if float(row.get(key)) > 0:
                return True
        except (TypeError, ValueError):
            continue
    return False


def audit_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    by_asset: dict[str, list[datetime]] = {}
    invalid_timestamps = 0
    prices = 0

    for row in rows:
        asset = str(row.get("source_id") or row.get("symbol") or row.get("id") or "")
        ts = _parse_ts(row.get("captured_at"))
        if not asset or ts is None:
            invalid_timestamps += 1
            continue
        by_asset.setdefault(asset, []).append(ts)
        if _positive_price(row):
            prices += 1

    intervals_hours: list[float] = []
    observations_per_asset: dict[str, int] = {}
    for asset, timestamps in by_asset.items():
        timestamps.sort()
        observations_per_asset[asset] = len(timestamps)
        for a, b in zip(timestamps, timestamps[1:]):
            delta = (b - a).total_seconds() / 3600
            if delta >= 0:
                intervals_hours.append(delta)

    def quantile(values: list[float], q: float) -> float | None:
        if not values:
            return None
        values = sorted(values)
        pos = (len(values) - 1) * q
        lo, hi = int(pos), min(int(pos) + 1, len(values) - 1)
        return values[lo] + (values[hi] - values[lo]) * (pos - lo)

    return {
        "total_rows": len(rows),
        "assets": len(by_asset),
        "valid_price_rows": prices,
        "invalid_timestamp_rows": invalid_timestamps,
        "observations_per_asset": observations_per_asset,
        "cadence_hours": {
            "min": min(intervals_hours) if intervals_hours else None,
            "median": quantile(intervals_hours, 0.5),
            "p95": quantile(intervals_hours, 0.95),
            "max": max(intervals_hours) if intervals_hours else None,
        },
        "horizon_observations_available": {
            str(h): sum(1 for count in observations_per_asset.values() if count > h)
            for h in (1, 6, 24, 72)
        },
    }
