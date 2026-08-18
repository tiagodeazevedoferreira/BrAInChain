"""Audit the effective future window used by supervised labels."""
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


def audit_temporal_coverage(rows: Iterable[Mapping[str, Any]], horizons_hours=(1, 6, 24, 72, 168)) -> dict[str, dict[str, int | float | None]]:
    """Measure future observations per asset, never across assets."""
    grouped: dict[str, list[datetime]] = {}
    for row in rows:
        captured = _ts(row.get("captured_at"))
        asset = row.get("source_id") or row.get("asset") or row.get("asset_id")
        if captured is not None and asset is not None:
            grouped.setdefault(str(asset), []).append(captured)

    for timestamps in grouped.values():
        timestamps.sort()

    result: dict[str, dict[str, int | float | None]] = {}
    for hours in horizons_hours:
        eligible = 0
        total_future = 0
        max_gap = None
        window_seconds = hours * 3600
        for timestamps in grouped.values():
            for index, start in enumerate(timestamps):
                future = [
                    timestamp for timestamp in timestamps[index + 1 :]
                    if (timestamp - start).total_seconds() <= window_seconds
                ]
                if future:
                    eligible += 1
                    total_future += len(future)
                    gap = max((timestamp - start).total_seconds() / 3600 for timestamp in future)
                    max_gap = gap if max_gap is None else max(max_gap, gap)
        result[f"{hours}h"] = {
            "eligible": eligible,
            "future_observations": total_future,
            "max_future_age_hours": max_gap,
        }
    return result
