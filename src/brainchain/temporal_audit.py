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
    ordered = sorted((dict(r) for r in rows if _ts(r.get("captured_at")) is not None), key=lambda r: _ts(r["captured_at"]))
    result: dict[str, dict[str, int | float | None]] = {}
    for hours in horizons_hours:
        eligible = 0
        total_future = 0
        max_gap = None
        for i, row in enumerate(ordered):
            start = _ts(row["captured_at"])
            if start is None:
                continue
            future_times = [_ts(other.get("captured_at")) for other in ordered[i + 1:]]
            future_times = [t for t in future_times if t is not None and (t - start).total_seconds() <= hours * 3600]
            if future_times:
                eligible += 1
                total_future += len(future_times)
                gap = max((t - start).total_seconds() / 3600 for t in future_times)
                max_gap = gap if max_gap is None else max(max_gap, gap)
        result[f"{hours}h"] = {
            "eligible": eligible,
            "future_observations": total_future,
            "max_future_age_hours": max_gap,
        }
    return result
