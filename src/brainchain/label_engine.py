"""Build future-looking training labels from historical crypto snapshots.

Labels describe what happened *after* an observation. They must never be used
as model features for that same observation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class LabelConfig:
    horizons_hours: tuple[int, ...] = (24, 168)
    multipliers: tuple[float, ...] = (2.0, 5.0, 10.0)


def _time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def build_labels(snapshots: Iterable[Mapping[str, Any]], config: LabelConfig | None = None) -> list[dict[str, Any]]:
    """Create point-in-time labels from snapshots grouped by source_id.

    A label is 1 when a future observed price reaches at least the configured
    multiplier of the current price within the horizon. If no future snapshot
    exists far enough to evaluate the horizon, the label is None rather than 0.
    """
    cfg = config or LabelConfig()
    rows = [dict(row) for row in snapshots if row.get("source_id") is not None and row.get("price_usd") is not None]
    groups: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["source_id"], []).append(row)

    output: list[dict[str, Any]] = []
    for coin_rows in groups.values():
        coin_rows.sort(key=lambda r: _time(r["captured_at"]))
        for index, current in enumerate(coin_rows):
            current_time = _time(current["captured_at"])
            current_price = float(current["price_usd"])
            labels: dict[str, Any] = {}
            future = coin_rows[index + 1 :]
            for horizon in cfg.horizons_hours:
                end = current_time.timestamp() + horizon * 3600
                eligible = [r for r in future if _time(r["captured_at"]).timestamp() <= end]
                # Do not label incomplete windows as failures.
                complete = bool(future and _time(future[-1]["captured_at"]).timestamp() >= end)
                for multiplier in cfg.multipliers:
                    key = f"target_{int(multiplier)}x_{horizon}h"
                    labels[key] = None if not complete else int(any(float(r["price_usd"]) >= current_price * multiplier for r in eligible))
            output.append({"source_id": current["source_id"], "captured_at": current["captured_at"], **labels})
    return output
