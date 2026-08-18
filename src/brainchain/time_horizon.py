"""Time-based future windows for irregular snapshot cadence."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping


def _parse(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def future_window(rows: Iterable[Mapping[str, Any]], start: datetime, hours: float) -> list[Mapping[str, Any]]:
    """Return observations strictly after start and within the requested horizon."""
    end = start + timedelta(hours=hours)
    result = []
    for row in rows:
        ts = _parse(row.get("captured_at"))
        if ts is not None and start < ts <= end:
            result.append(row)
    return sorted(result, key=lambda r: _parse(r.get("captured_at")) or start)
