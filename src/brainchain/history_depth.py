"""Measure historical depth per asset."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping


def _ts(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def audit_history_depth(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    by_asset: dict[str, list[datetime]] = {}
    for row in rows:
        asset = row.get("source_id")
        ts = _ts(row.get("captured_at"))
        if asset is None or ts is None:
            continue
        by_asset.setdefault(str(asset), []).append(ts)

    durations = []
    snapshot_counts = []
    for timestamps in by_asset.values():
        timestamps.sort()
        durations.append((timestamps[-1] - timestamps[0]).total_seconds() / 3600)
        snapshot_counts.append(len(timestamps))

    durations.sort()
    snapshot_counts.sort()

    def percentile(values: list[float], p: float) -> float | None:
        if not values:
            return None
        if len(values) == 1:
            return values[0]
        pos = (len(values) - 1) * p
        lo, hi = int(pos), min(int(pos) + 1, len(values) - 1)
        frac = pos - lo
        return values[lo] + (values[hi] - values[lo]) * frac

    return {
        "assets": len(durations),
        "history_hours": {
            "min": min(durations) if durations else None,
            "p25": percentile(durations, 0.25),
            "median": percentile(durations, 0.50),
            "p75": percentile(durations, 0.75),
            "p95": percentile(durations, 0.95),
            "max": max(durations) if durations else None,
        },
        "snapshots_per_asset": {
            "min": min(snapshot_counts) if snapshot_counts else None,
            "median": percentile([float(x) for x in snapshot_counts], 0.50),
            "max": max(snapshot_counts) if snapshot_counts else None,
        },
        "assets_with_1h_history": sum(x >= 1 for x in durations),
        "assets_with_6h_history": sum(x >= 6 for x in durations),
        "assets_with_24h_history": sum(x >= 24 for x in durations),
        "assets_with_72h_history": sum(x >= 72 for x in durations),
        "assets_with_168h_history": sum(x >= 168 for x in durations),
    }
