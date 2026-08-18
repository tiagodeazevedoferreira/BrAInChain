"""Estimate when the collected history can support each training horizon."""
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


def audit_readiness(rows: Iterable[Mapping[str, Any]], horizons=(1, 6, 24, 72, 168)) -> dict[str, Any]:
    by_asset: dict[str, list[datetime]] = {}
    for row in rows:
        asset = row.get("source_id") or row.get("asset") or row.get("asset_id")
        ts = _ts(row.get("captured_at"))
        if asset is not None and ts is not None:
            by_asset.setdefault(str(asset), []).append(ts)

    durations = []
    cadences = []
    for timestamps in by_asset.values():
        timestamps.sort()
        durations.append((timestamps[-1] - timestamps[0]).total_seconds() / 3600)
        cadences.extend(
            (b - a).total_seconds() / 3600
            for a, b in zip(timestamps, timestamps[1:])
            if b > a
        )

    now = max((ts for values in by_asset.values() for ts in values), default=None)
    durations.sort()
    cadences.sort()

    def median(values: list[float]) -> float | None:
        if not values:
            return None
        n = len(values)
        m = n // 2
        return values[m] if n % 2 else (values[m - 1] + values[m]) / 2

    max_history = max(durations) if durations else 0.0
    result: dict[str, Any] = {
        "assets": len(durations),
        "observations": sum(len(v) for v in by_asset.values()),
        "latest_observation": now.isoformat() if now else None,
        "median_cadence_hours": median(cadences),
        "max_history_hours": max_history,
        "horizons": {},
    }
    for horizon in horizons:
        eligible = sum(d >= horizon for d in durations)
        remaining = max(0.0, horizon - max_history)
        result["horizons"][f"{horizon}h"] = {
            "assets_with_history": eligible,
            "hours_until_first_asset": remaining,
        }
    return result
